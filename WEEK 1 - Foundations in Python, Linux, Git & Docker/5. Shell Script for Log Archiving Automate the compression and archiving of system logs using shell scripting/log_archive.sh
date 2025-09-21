#!/bin/bash

# =====================================================
# Advanced Log Archiving Script with Rotation & Logging
# Author : Siva Balaji (Ascendion Assignment)
# =====================================================

# === CONFIGURATION ===
BASE_DIR="/c/Users/sivabalaji.vm/Desktop/Ascendion/Assignments/WEEK 1 - Foundations in Python, Linux, Git & Docker/5. Shell Script for Log Archiving Automate the compression and archiving of system logs using shell scripting"
LOG_DIR="$BASE_DIR/logs"                # Folder containing .log files
ARCHIVE_DIR="$BASE_DIR/logs_archive"    # Folder to store archives
RETENTION_DAYS=7                        # Keep archives for 7 days
ACTION_LOG="$BASE_DIR/archive_actions.log" # Log file for script actions

# === COLORS ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# === TIMESTAMP ===
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
ARCHIVE_FILE="$ARCHIVE_DIR/logs_$DATE.tar.gz"

# === Ensure archive directory exists ===
mkdir -p "$ARCHIVE_DIR"

echo -e "${CYAN}=============================================="
echo -e " Starting Advanced Log Archiving Script"
echo -e " Timestamp: $DATE"
echo -e " Logs Directory: $LOG_DIR"
echo -e " Archive Destination: $ARCHIVE_FILE"
echo -e " Retention: $RETENTION_DAYS days"
echo -e "==============================================${NC}"

# === Check for logs ===
if ls "$LOG_DIR"/*.log 1> /dev/null 2>&1; then
    echo -e "${YELLOW}Archiving logs...${NC}"
    
    # Compress logs
    tar -czf "$ARCHIVE_FILE" -C "$LOG_DIR" .

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Archive created: $ARCHIVE_FILE${NC}"
        echo "[$DATE] Archived logs to $ARCHIVE_FILE" >> "$ACTION_LOG"

        # Rotate logs (clear contents after archiving)
        echo -e "${YELLOW}Rotating logs (clearing old content)...${NC}"
        for file in "$LOG_DIR"/*.log; do
            > "$file"
            echo "[$DATE] Cleared $file" >> "$ACTION_LOG"
        done
        echo -e "${GREEN}✅ Logs rotated successfully.${NC}"
    else
        echo -e "${RED}❌ Failed to create archive.${NC}"
        echo "[$DATE] ERROR: Failed to create archive" >> "$ACTION_LOG"
        exit 1
    fi
else
    echo -e "${RED}⚠️ No .log files found in $LOG_DIR${NC}"
    echo "[$DATE] WARNING: No logs found" >> "$ACTION_LOG"
    exit 0
fi

# === Delete old archives ===
echo -e "${YELLOW}Cleaning up archives older than $RETENTION_DAYS days...${NC}"
find "$ARCHIVE_DIR" -name "*.tar.gz" -type f -mtime +$RETENTION_DAYS -exec rm {} \; -exec echo "[$DATE] Deleted {}" >> "$ACTION_LOG" \;

echo -e "${GREEN}🎉 Log Archiving Completed Successfully!${NC}"
echo -e "📜 Actions logged in: $ACTION_LOG"
