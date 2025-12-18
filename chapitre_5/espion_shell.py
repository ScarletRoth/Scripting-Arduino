from __future__ import annotations

import argparse
import os
import queue
import random
import signal
import sys
import time
from multiprocessing import Event, Process, Queue

def worker_loop(*, idx: int, interval_s: float, stop_event: Event, out_q: Queue) -> None:
	pid = os.getpid()
	try:
		while not stop_event.is_set():
			val = random.randint(0, 1_000_000)
			ts = time.time()
			try:
				out_q.put((pid, idx, val, ts), timeout=0.2)
			except Exception:
				pass
			time.sleep(interval_s)
	finally:
		return

def _install_parent_signal_handlers(stop_event: Event) -> None:
	def _handler(signum, frame):
		stop_event.set()
	for sig in (signal.SIGINT, signal.SIGTERM):
		try:
			signal.signal(sig, _handler)
		except Exception:
			pass

def main(argv: list[str]) -> int:
	parser = argparse.ArgumentParser(
		description="Démarre N processus générant des nombres aléatoires (multiprocessing) + arrêt propre."
	)
	parser.add_argument("-n", "--num-procs", type=int, default=4, help="Nombre de workers à lancer (défaut: 4)")
	parser.add_argument(
		"-i",
		"--interval",
		type=float,
		default=1.0,
		help="Intervalle en secondes entre 2 nombres (défaut: 1.0)",
	)
	parser.add_argument(
		"--no-print",
		action="store_true",
		help="Ne pas afficher les valeurs (utile si vous voulez seulement observer via ps).",
	)
	parser.add_argument(
		"--join-timeout",
		type=float,
		default=3.0,
		help="Temps d'attente (s) pour join() avant terminate() (défaut: 3.0)",
	)
	args = parser.parse_args(argv)

	if args.num_procs <= 0:
		print("num-procs doit être > 0", file=sys.stderr)
		return 2
	if args.interval <= 0:
		print("interval doit être > 0", file=sys.stderr)
		return 2

	stop_event = Event()
	_install_parent_signal_handlers(stop_event)
	out_q: Queue = Queue(maxsize=10_000)
	procs: list[Process] = []
	parent_pid = os.getpid()
	for i in range(args.num_procs):
		p = Process(
			target=worker_loop,
			kwargs={"idx": i, "interval_s": args.interval, "stop_event": stop_event, "out_q": out_q},
			name=f"rng-worker-{i}",
			daemon=False,
		)
		p.start()
		procs.append(p)

	print(f"[parent] pid={parent_pid} started {len(procs)} workers:", flush=True)
	for p in procs:
		print(f"  - name={p.name} pid={p.pid}", flush=True)

	print(
		"\nDepuis un autre shell (Linux/macOS/WSL), exemples:\n"
		"  ps -o pid,ppid,stat,etime,cmd -p <PID_PARENT>\n"
		"  ps -o pid,ppid,stat,etime,cmd --ppid <PID_PARENT>\n"
		"  ps aux | grep espion_shell.py\n"
		"  ps aux | grep rng-worker-\n"
		"Depuis un autre CMD (Windows), exemples:\n"
		"  tasklist /FI IMAGENAME eq python.exe\n"
		"  for /L %i in () do @(tasklist /FI IMAGENAME eq python.exe & timeout /T 1 > nul & cls)\n",
		flush=True,
	)

	try:
		while not stop_event.is_set():
			try:
				pid, idx, val, ts = out_q.get(timeout=0.5)
				if not args.no_print:
					print(f"[recv] worker#{idx} pid={pid} val={val} t={ts:.3f}", flush=True)
			except queue.Empty:
				pass
			for p in procs:
				if p.exitcode is not None and p.exitcode != 0:
					print(f"[parent] worker {p.name} pid={p.pid} exited with code={p.exitcode} -> stopping", flush=True)
					stop_event.set()
					break
				
	except KeyboardInterrupt:
		stop_event.set()
	finally:
		print("[parent] stopping workers...", flush=True)
		stop_event.set()
		deadline = time.time() + args.join_timeout
		for p in procs:
			remaining = max(0.0, deadline - time.time())
			p.join(timeout=remaining)
		for p in procs:
			if p.is_alive():
				print(f"[parent] terminate {p.name} pid={p.pid}", flush=True)
				p.terminate()
		for p in procs:
			p.join(timeout=1.0)

		print("[parent] done.", flush=True)
	return 0
if __name__ == "__main__":
	raise SystemExit(main(sys.argv[1:]))