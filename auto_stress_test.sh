#!/bin/bash

operations=("post" "get")
sizes=(10 50 100)
clients=(1 5 50)

for operation in "${operations[@]}"; do
    read -p "Jalankan operasi ${operation} sekarang? (y/n): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "Operasi dibatalkan."
        continue
    fi

    for size in "${sizes[@]}"; do
        for client in "${clients[@]}"; do
            echo -e "\nTesting ${operation} with ${size}MB and ${client} clients\n"
            python file_client_stress.py --operation "$operation" --size "$size" --clients "$client"
        done
    done
done
