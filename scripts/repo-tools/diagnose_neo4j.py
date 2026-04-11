#!/usr/bin/env python3
import socket
import ssl
import requests
from urllib.parse import urlparse

def test_neo4j_connectivity():
    uri = "neo4j+s://371530ba.databases.neo4j.io"
    
    print("🔍 DIAGNOSING NEO4J AURA CONNECTIVITY")
    print("=" * 50)
    
    # Parse the URI
    parsed = urlparse(uri.replace("neo4j+s://", "https://"))
    hostname = parsed.hostname
    port = 7687  # Standard Neo4j port for bolt+s
    
    print(f"Target: {hostname}:{port}")
    
    # 1. DNS Resolution Test
    print(f"\n1. DNS Resolution for {hostname}")
    try:
        ip = socket.gethostbyname(hostname)
        print(f"   ✅ Resolved to: {ip}")
    except Exception as e:
        print(f"   ❌ DNS failed: {e}")
        return
    
    # 2. TCP Connection Test
    print(f"\n2. TCP Connection to {hostname}:{port}")
    try:
        sock = socket.create_connection((hostname, port), timeout=10)
        sock.close()
        print(f"   ✅ TCP connection successful")
    except Exception as e:
        print(f"   ❌ TCP connection failed: {e}")
        return
    
    # 3. SSL/TLS Test
    print(f"\n3. SSL/TLS Handshake")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                print(f"   ✅ SSL handshake successful")
                print(f"   📜 Certificate subject: {cert.get('subject')}")
    except Exception as e:
        print(f"   ❌ SSL handshake failed: {e}")
        return
    
    # 4. HTTP Health Check (if available)
    print(f"\n4. HTTP Health Check")
    try:
        health_url = f"https://{hostname}:7474/db/data/"  # Neo4j HTTP interface
        response = requests.get(health_url, timeout=10)
        print(f"   ✅ HTTP health check: {response.status_code}")
    except Exception as e:
        print(f"   ❌ HTTP health check failed: {e}")
    
    # 5. Neo4j Driver Test with Different Strategies
    print(f"\n5. Neo4j Driver Tests")
    
    from neo4j import GraphDatabase
    
    configs = [
        {"encrypted": True, "trust": "TRUST_ALL_CERTIFICATES"},
        {"encrypted": True, "trust": "TRUST_SYSTEM_CA_SIGNED_CERTIFICATES"},
        {"encrypted": True}
    ]
    
    for i, config in enumerate(configs, 1):
        try:
            print(f"   Config {i}: {config}")
            driver = GraphDatabase.driver(
                uri, 
                auth=("neo4j", "mostar123"),
                **config
            )
            with driver.session() as session:
                result = session.run("RETURN 1 AS test")
                record = result.single()
                if record and record["test"] == 1:
                    print(f"   ✅ Config {i} SUCCESS!")
                    driver.close()
                    return True
            driver.close()
        except Exception as e:
            print(f"   ❌ Config {i} failed: {e}")
    
    return False

if __name__ == "__main__":
    success = test_neo4j_connectivity()
    
    print(f"\n" + "=" * 50)
    if success:
        print("🎉 Neo4j Aura connection is working!")
    else:
        print("❌ Neo4j Aura connection failed.")
        print("\nPossible causes:")
        print("- Neo4j Aura instance is paused/suspended")
        print("- Credentials are incorrect")
        print("- Firewall blocking bolt+s port 7687")
        print("- Network connectivity issues")
        print("- Instance doesn't exist or was deleted")
