open Astring

module Request = Cohttp_lwt_unix.Request
module Response = Cohttp_lwt_unix.Response
module Server = Cohttp_lwt_unix.Server

let read_file path =
  let ch = open_in path in
  let data = really_input_string ch (in_channel_length ch) in
  close_in ch;
  data

let homepage = read_file "index.html"

let load_db path =
  let data = read_file path in
  let lines = String.cuts ~sep:"\n" ~empty:false data |> List.map String.trim in
  String.Set.of_list lines

let debian = load_db "debian.db"
let debian_maint = load_db "debian-maintainers.db"

let elem writer name ?(attrs=[]) children =
  Xmlm.output writer @@ `El_start (("", name), attrs);
  children ();
  Xmlm.output writer @@ `El_end

let string_of_vote = function
  | `Good -> "good"

let report writer ~vote msg =
  let attrs = [ ("", "vote"), string_of_vote vote ] in
  elem writer "item" ~attrs (fun () -> Xmlm.output writer @@ `Data msg)

let lookup_key key =
  let headers = Cohttp.Header.(add (init ())) "Content-Type" "application/xml" in
  let b = Buffer.create 1024 in
  let writer = Xmlm.make_output (`Buffer b) in
  Xmlm.output writer @@ `Dtd None;
  elem writer "key-lookup" (fun () ->
      String.Map.find_opt key Trust_db.hints |> Option.iter (report writer ~vote:`Good);
      if String.Set.mem key debian then report writer ~vote:`Good "This key belongs to a Debian Developer.";
      if String.Set.mem key debian_maint then report writer ~vote:`Good "This key belongs to a Debian Maintainer.";
    );
  let body = Buffer.contents b in
  Server.respond_string ~headers ~body ~status:`OK ()

let pp_timestamp f x =
  let open Unix in
  let tm = localtime x in
  Format.fprintf f "%04d-%02d-%02d %02d:%02d.%02d" (tm.tm_year + 1900) (tm.tm_mon + 1)
    tm.tm_mday tm.tm_hour tm.tm_min tm.tm_sec

let callback _conn req _body =
  let uri = Request.uri req in
  Lwt.catch
    (fun () ->
       let meth = Request.meth req in
       let path = Uri.path uri in
       let time = Unix.gettimeofday () in
       Format.printf "%a: HTTP %s %S@." pp_timestamp time (Cohttp.Code.string_of_method meth) path;
       match meth, String.cuts ~empty:false ~sep:"/" path with
       | `GET, ([] | ["index.html"]) -> Server.respond_string ~body:homepage ~status:`OK ()
       | `GET, ["key"; key] -> lookup_key key
       | `GET, _ -> Server.respond_not_found ()
       | _ -> Server.respond_error ~status:`Bad_request ~body:"Bad method" ()
    )
    (fun ex ->
       Format.eprintf "Error handling request for %a: %s@." Uri.pp uri (Printexc.to_string ex);
       raise ex
    )

let () =
  Lwt_main.run begin
    print_endline "Service ready";
    Server.create ~mode:(`TCP (`Port 8000)) (Server.make ~callback ())
  end
