#!/usr/bin/env bash

echo "📦 Creating replication package..."
tar -czvf replication_package.tar.gz results/ benchmarks/ scripts/ configs/ env_setup/
echo "✅ Replication package created!"
