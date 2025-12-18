#chapitre 13

import smtplib

def prompt(title):
    return input(title).strip()

from_addr = prompt("From: matteo.linglet@ynov.com")
to_addrs  = prompt("To: matteo.liglet@gmail.com").split()
print("Coucou c'est un test^D")

lines = [f"From: {from_addr}", f"To: {', '.join(to_addrs)}", ""]
while True:
    try:
        line = input()
    except (EOFError, KeyboardInterrupt):
        break
    else:
        lines.append(line)

msg = "\r\n".join(lines)
print("Message length is", len(msg))

server = smtplib.SMTP("localhost")
server.set_debuglevel(1)
server.sendmail(from_addr, to_addrs, msg)
server.quit()