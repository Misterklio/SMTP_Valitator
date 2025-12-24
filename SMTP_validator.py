import sys
import smtplib
import socket
import ssl
import argparse
import random
import time
import threading
banner_art = """                                                                   
 ▄▄▄▄▄▄▄ ▄▄▄      ▄▄▄ ▄▄▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄     ▄▄▄▄  ▄▄▄▄   ▄▄▄▄   ▄▄▄      ▄▄▄▄▄ ▄▄▄▄▄▄   
█████▀▀▀ ████▄  ▄████ ▀▀▀███▀▀▀ ███▀▀███▄   ▀███  ███▀ ▄██▀▀██▄ ███       ███  ███▀▀██▄ 
 ▀████▄  ███▀████▀███    ███    ███▄▄███▀    ███  ███  ███  ███ ███       ███  ███  ███ 
   ▀████ ███  ▀▀  ███    ███    ███▀▀▀▀      ███▄▄███  ███▀▀███ ███       ███  ███  ███ [Coded By Mister klio]
███████▀ ███      ███    ███    ███           ▀████▀   ███  ███ ████████ ▄███▄ ██████▀  [Github: Misterklio]
"""
def check_smtp(server, port, user, password, timeout=10, verbose=False):
    try:
        if port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(server, port, timeout=timeout, context=context) as smtp:
                if verbose:
                    smtp.set_debuglevel(1)
                smtp.login(user, password)
                return True, None, "Login successful"
        else:
            with smtplib.SMTP(server, port, timeout=timeout) as smtp:
                if verbose:
                    smtp.set_debuglevel(1)
                smtp.ehlo()
                try:
                    smtp.starttls(context=ssl.create_default_context())
                    smtp.ehlo()
                except smtplib.SMTPNotSupportedError:
                    pass
                smtp.login(user, password)
                return True, None, "Login successful"
    except smtplib.SMTPAuthenticationError as e:
        msg = e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else str(e.smtp_error)
        return False, e.smtp_code, msg
    except smtplib.SMTPResponseException as e:
        msg = e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else str(e.smtp_error)
        return False, e.smtp_code, msg
    except (socket.error, socket.timeout, ssl.SSLError) as e:
        return False, None, str(e)
    except smtplib.SMTPException as e:
        return False, None, str(e)
    except Exception as e:
        return False, None, str(e)


def parse_line(line):
    parts = [p.strip() for p in line.strip().split('|')]
    if len(parts) != 4:
        return None
    server = parts[0].rstrip(':')
    try:
        port = int(parts[1])
    except ValueError:
        return None
    user = parts[2]
    password = parts[3]
    return server, port, user, password


def main():
    parser = argparse.ArgumentParser(prog="checker.py", add_help=True)
    parser.add_argument("path", help="Path to list.txt")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--reasons", action="store_true", help="Show failure reasons")
    parser.add_argument("--verbose", action="store_true", help="Enable SMTP debug output")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--no-shuffle", action="store_true", help="Disable random scan order")
    parser.add_argument("--no-dedupe", action="store_true", help="Disable deduplication")
    args = parser.parse_args()

    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    CHARTREUSE = "\x1b[38;2;127;255;0m"
    GOLD = "\x1b[38;2;255;215;0m"
    GHOSTWHITE = "\x1b[38;2;248;248;255m"
    CRIMSON = "\x1b[38;2;220;20;60m"
    GREY = "\x1b[38;2;169;169;169m"
    RESET = "\x1b[0m"
    if args.no_color:
        RED = GREEN = YELLOW = CHARTREUSE = GOLD = GHOSTWHITE = CRIMSON = GREY = RESET = ""

    print(f"{CHARTREUSE}{banner_art}{RESET}")

    path = args.path
    try:
        with open(path, 'r', encoding='utf-8') as file, open('valid_smtp.txt', 'a', encoding='utf-8') as out:
            entries = []
            seen = set()
            for line in file:
                raw = line.rstrip("\n")
                s = raw.strip()
                if not s or s.startswith('#'):
                    continue
                parsed = parse_line(s)
                if not parsed:
                    print(f"Skip: {raw}")
                    continue
                server, port, user, password = parsed
                key = (server, port, user, password)
                if args.no_dedupe or key not in seen:
                    entries.append((server, port, user, password))
                    seen.add(key)
            if not args.no_shuffle:
                random.shuffle(entries)
            for server, port, user, password in entries:
                print(f"{GOLD}Scanning:{RESET} {GREEN}{server}:{port}{RESET} - {GREY}[{user}]{RESET}", flush=True)
                stop_event = threading.Event()
                def spin():
                    i = 0
                    dots = ["...", "..", "."]
                    while not stop_event.is_set():
                        d = dots[i % len(dots)]
                        print(f"\r{CHARTREUSE}Please wait {d}{RESET}", end="", flush=True)
                        time.sleep(0.3)
                        i += 1
                t = threading.Thread(target=spin, daemon=True)
                t.start()
                ok, code, msg = check_smtp(server, port, user, password, timeout=args.timeout, verbose=args.verbose)
                stop_event.set()
                t.join()
                print("\r" + " " * 80 + "\r", end="", flush=True)
                if ok:
                    print(f"{CHARTREUSE}Login successful:{RESET} {GREEN}{server}:{port}{RESET} - {GREY}[{user}]{RESET}", flush=True)
                    out.write(f"{server}|{port}|{user}|{password}\n")
                    out.flush()
                else:
                    if args.reasons:
                        reason = f" (code={code}, reason={msg})" if code is not None else f" (reason={msg})"
                        print(f"{CRIMSON}Failed:{RESET} {GREEN}{server}:{port}{RESET} - {GREY}[{user}]{RESET}{reason}", flush=True)
                    else:
                        print(f"{CRIMSON}Failed:{RESET} {GREEN}{server}:{port}{RESET} - {GREY}[{user}]{RESET}", flush=True)
                    if "office365.com" in server and server != "smtp.office365.com":
                        print(f"{GHOSTWHITE}Retry scanning:{RESET} {GREEN}smtp.office365.com:{port}{RESET} - {GREY}[{user}]{RESET}", flush=True)
                        stop_event2 = threading.Event()
                        def spin2():
                            i = 0
                            dots = ["...", "..", "."]
                            while not stop_event2.is_set():
                                d = dots[i % len(dots)]
                                print(f"\r{CHARTREUSE}Please wait {d}{RESET}", end="", flush=True)
                                time.sleep(0.3)
                                i += 1
                        t2 = threading.Thread(target=spin2, daemon=True)
                        t2.start()
                        ok2, code2, msg2 = check_smtp("smtp.office365.com", port, user, password, timeout=args.timeout, verbose=args.verbose)
                        stop_event2.set()
                        t2.join()
                        print("\r" + " " * 80 + "\r", end="", flush=True)
                        if ok2:
                            print(f"{CHARTREUSE}Login successful:{RESET} {GREEN}smtp.office365.com:{port}{RESET} - {GREY}[{user}]{RESET}", flush=True)
                            out.write(f"smtp.office365.com|{port}|{user}|{password}\n")
                            out.flush()
                        else:
                            if args.reasons:
                                r2 = f" (code={code2}, reason={msg2})" if code2 is not None else f" (reason={msg2})"
                                print(f"{CRIMSON}Failed:{RESET} {GREEN}smtp.office365.com:{port}{RESET} - {GREY}[{user}]{RESET}{r2}", flush=True)
                            else:
                                print(f"{CRIMSON}Failed:{RESET} {GREEN}smtp.office365.com:{port}{RESET} - {GREY}[{user}]{RESET}", flush=True)
    except FileNotFoundError:
        print(f"File not found: {path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
