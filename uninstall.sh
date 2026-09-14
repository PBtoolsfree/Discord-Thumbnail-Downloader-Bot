#!/bin/bash
echo "WARNING: This will completely remove the bot containers and images."
read -p "Are you sure? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    docker compose down --rmi all
    echo "Bot uninstalled. To remove data, delete the 'data' and 'tmp' directories manually."
fi
