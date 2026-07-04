import time
import json
import urllib.request
import urllib.error
import subprocess
import socket
import sys
import random
import uuid
from typing import Dict, List, Tuple, Any, Optional

def check_port_8080() -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect(("127.0.0.1", 8080))
        s.close()
        return True
    except (ConnectionRefusedError, socket.timeout):
        return False

def make_multipart_body(fields: Dict[str, str], boundary: str = "Boundary---1234567890") -> Tuple[bytes, str]:
    body = b""
    for name, value in fields.items():
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        body += f"{value}\r\n".encode()
    body += f"--{boundary}--\r\n".encode()
    content_type = f"multipart/form-data; boundary={boundary}"
    return body, content_type

def run_request(url: str, method: str = "GET", fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    req_fields = fields if fields is not None else {}
    
    body, content_type = make_multipart_body(req_fields)
    req = urllib.request.Request(
        url,
        data=body if method == "POST" or fields else None,
        headers={"Content-Type": content_type} if fields else {},
        method=method
    )
    
    t_start = time.perf_counter()
    try:
        with urllib.request.urlopen(req) as res:
            res_data = res.read().decode()
            t_end = time.perf_counter()
            rtt = (t_end - t_start) * 1000
            
            try:
                parsed = json.loads(res_data)
                if isinstance(parsed, dict) and "benchmark" in parsed:
                    srv = parsed["benchmark"]
                    return {
                        "success": True,
                        "rtt": rtt,
                        "parsing": float(srv["parsing_ms"]),
                        "routing": float(srv["routing_ms"]),
                        "operation": float(srv["operation_ms"]),
                        "send": float(srv["response_send_ms"]),
                        "data": parsed.get("data"),
                        "error": None
                    }
            except Exception:
                pass
            return {"success": True, "rtt": rtt, "parsing": 0.0, "routing": 0.0, "operation": 0.0, "send": 0.0, "data": None, "error": None}
    except Exception as e:
        return {"success": False, "error": str(e), "rtt": 0.0, "parsing": 0.0, "routing": 0.0, "operation": 0.0, "send": 0.0, "data": None}

def run_comparison() -> None:
    print("\n" + "=" * 60)
    print("  NETWORKING ANALYSIS: 127.0.0.1 vs localhost")
    print("=" * 60)
    print("Testing loopback address vs named resolution (10 iterations)...")
    
    ip_rtts: List[float] = []
    host_rtts: List[float] = []
    
    for _ in range(10):
        # 127.0.0.1
        t_start = time.perf_counter()
        try:
            req = urllib.request.Request("http://127.0.0.1:8080/", headers={"Content-Type": "multipart/form-data; boundary=Boundary---1234567890"})
            with urllib.request.urlopen(req) as res:
                res.read()
                ip_rtts.append((time.perf_counter() - t_start) * 1000)
        except Exception:
            pass
            
        # localhost
        t_start = time.perf_counter()
        try:
            req = urllib.request.Request("http://localhost:8080/", headers={"Content-Type": "multipart/form-data; boundary=Boundary---1234567890"})
            with urllib.request.urlopen(req) as res:
                res.read()
                host_rtts.append((time.perf_counter() - t_start) * 1000)
        except Exception:
            pass
            
        time.sleep(0.01)
        
    if ip_rtts and host_rtts:
        avg_ip = sum(ip_rtts) / len(ip_rtts)
        avg_host = sum(host_rtts) / len(host_rtts)
        print(f"Average RTT (http://127.0.0.1:8080/): {avg_ip:.3f} ms")
        print(f"Average RTT (http://localhost:8080/): {avg_host:.3f} ms")
        diff = avg_host - avg_ip
        print(f"Difference: {diff:+.3f} ms")
        if diff > 10:
            print("\n[!] NOTICE: 'localhost' is significantly slower than '127.0.0.1'.")
            print("    This is typically caused by IPv6 loopback [::1] timeout/fallback on your OS.")
            print("    Try using '127.0.0.1' in Postman/curl instead of 'localhost'!")
        else:
            print("\n[+] Loopback latency is consistent. No IPv6 resolution issues detected.")
    else:
        print("[-] Could not complete comparison test.")
    print("=" * 60 + "\n")

def run_benchmark(target: int = 50, warmup: int = 300) -> None:
    print("=" * 60)
    print("  TODO SERVER BENCHMARK SUITE (MIXED LIFECYCLE SIMULATION)")
    print("=" * 60)
    
    created_todo_ids: List[str] = []

    # 1. Warmup Phase: Pre-populate items
    print(f"[*] Pre-populating database with {warmup} random items...")
    for i in range(warmup):
        todo_content = f"Warmup-{uuid.uuid4()}"
        res = run_request("http://127.0.0.1:8080/add-todo", "POST", {"todo": todo_content, "benchmarking": "yes"})
        if res["success"]:
            todos_list = res.get("data", [])
            if isinstance(todos_list, list):
                for item in todos_list:
                    if isinstance(item, dict) and item.get("todo") == todo_content:
                        todo_id = item.get("todoId")
                        if todo_id:
                            created_todo_ids.append(str(todo_id))
                        break
        if (i + 1) % 50 == 0 or (i + 1) == warmup:
            print(f"    Added {i + 1}/{warmup} items...")
    
    print(f"[+] Warmup finished. Starting benchmark loop. Target: {target} iterations per operation.")

    # Counters and metrics dictionary
    counters = {
        "GET /": 0,
        "GET /fetch-todos": 0,
        "POST /add-todo": 0,
        "POST /remove-todo": 0
    }
    
    metrics: Dict[str, Dict[str, List[float]]] = {
        "GET /": {"rtt": [], "parsing": [], "routing": [], "operation": [], "send": []},
        "GET /fetch-todos": {"rtt": [], "parsing": [], "routing": [], "operation": [], "send": []},
        "POST /add-todo": {"rtt": [], "parsing": [], "routing": [], "operation": [], "send": []},
        "POST /remove-todo": {"rtt": [], "parsing": [], "routing": [], "operation": [], "send": []}
    }

    total_runs = 0
    while any(count < target for count in counters.values()):
        # Select operation completely at random between 1 and 1000
        r = random.randint(1, 1000)
        
        op = ""
        url = ""
        method = ""
        fields: Optional[Dict[str, str]] = None
        
        if 1 <= r <= 250:
            op = "GET /"
            url = "http://127.0.0.1:8080/"
            method = "GET"
            fields = {"benchmarking": "yes"}
        elif 251 <= r <= 500:
            op = "GET /fetch-todos"
            url = "http://127.0.0.1:8080/fetch-todos"
            method = "GET"
            fields = {"benchmarking": "yes"}
        elif 501 <= r <= 750:
            op = "POST /add-todo"
            url = "http://127.0.0.1:8080/add-todo"
            method = "POST"
            todo_val = f"Task-{uuid.uuid4()}"
            fields = {"todo": todo_val, "benchmarking": "yes"}
        else:
            # POST /remove-todo
            if not created_todo_ids:
                # Edge case: No items exist to delete, roll again
                continue
            op = "POST /remove-todo"
            url = "http://127.0.0.1:8080/remove-todo"
            method = "POST"
            selected_id = random.choice(created_todo_ids)
            fields = {"todoId": selected_id, "benchmarking": "yes"}

        # Fire request
        res = run_request(url, method, fields)
        
        if res["success"]:
            # Increment specific counter
            counters[op] += 1
            total_runs += 1
            
            # Save metrics
            metrics[op]["rtt"].append(res["rtt"])
            metrics[op]["parsing"].append(res["parsing"])
            metrics[op]["routing"].append(res["routing"])
            metrics[op]["operation"].append(res["operation"])
            metrics[op]["send"].append(res["send"])
            
            # Post-request state updates
            if op == "POST /add-todo":
                todos_list = res.get("data", [])
                if isinstance(todos_list, list) and fields:
                    added_title = fields.get("todo")
                    for item in todos_list:
                        if isinstance(item, dict) and item.get("todo") == added_title:
                            todo_id = item.get("todoId")
                            if todo_id:
                                created_todo_ids.append(str(todo_id))
                            break
            elif op == "POST /remove-todo" and fields:
                deleted_id = fields.get("todoId")
                if deleted_id in created_todo_ids:
                    created_todo_ids.remove(deleted_id)
                    
        time.sleep(0.001)

    print(f"\n[+] Benchmark loop completed in {total_runs} total requests.")

    # Print results
    print("=" * 75)
    print("  SIMULATION RESULTS SUMMARY")
    print("=" * 75)
    for op_name, op_metrics in metrics.items():
        print(f"\nResults for {op_name} (Executed {counters[op_name]} times):")
        rtt_list = op_metrics["rtt"]
        if not rtt_list:
            print("  No successful requests.")
            continue
        print("-" * 75)
        print(f"{'Metric':<20} | {'Min (ms)':<10} | {'Max (ms)':<10} | {'Avg (ms)':<10} | {'Median (ms)':<10}")
        print("-" * 75)
        for label, lst in [
            ("Parsing", op_metrics["parsing"]),
            ("Routing", op_metrics["routing"]),
            ("Operation", op_metrics["operation"]),
            ("Response Send", op_metrics["send"]),
            ("Round-Trip (RTT)", rtt_list)
        ]:
            min_val = min(lst)
            max_val = max(lst)
            avg_val = sum(lst) / len(lst)
            median_val = sorted(lst)[len(lst) // 2]
            print(f"{label:<20} | {min_val:<10.3f} | {max_val:<10.3f} | {avg_val:<10.3f} | {median_val:<10.3f}")
        print("-" * 75)

if __name__ == "__main__":
    target_count = 50
    if len(sys.argv) > 1:
        try:
            target_count = int(sys.argv[1])
        except ValueError:
            pass
    else:
        if sys.stdin.isatty():
            try:
                val = input("Enter target iteration count for each operation [50]: ")
                target_count = int(val) if val.strip() else 50
            except (ValueError, KeyboardInterrupt, EOFError):
                pass

    warmup_count = 300
    if len(sys.argv) > 2:
        try:
            warmup_count = int(sys.argv[2])
        except ValueError:
            pass
    else:
        if sys.stdin.isatty():
            try:
                val = input("Enter number of todo items to pre-populate [300]: ")
                warmup_count = int(val) if val.strip() else 300
            except (ValueError, KeyboardInterrupt, EOFError):
                pass

    server_process = None
    if not check_port_8080():
        print("[*] Port 8080 is closed. Starting server.py automatically...")
        server_process = subprocess.Popen(
            [".venv/bin/python", "server.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        for _ in range(20):
            time.sleep(0.1)
            if check_port_8080():
                print("[+] Server started successfully!")
                break
        else:
            print("[-] Failed to start the server. Exiting.")
            server_process.terminate()
            sys.exit(1)
            
    try:
        run_benchmark(target_count, warmup_count)
        run_comparison()
    finally:
        if server_process:
            print("[*] Stopping server...")
            server_process.terminate()
            server_process.wait()
            print("[+] Server stopped.")
