#!/bin/bash
#
# Monitor Hadith Downloads
# Shows progress and estimates completion time
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

BUKHARI_FILE="$PROJECT_ROOT/data/corpus/raw/bukhari/bukhari_hadiths.jsonl"
MUSLIM_FILE="$PROJECT_ROOT/data/corpus/raw/muslim/muslim_hadiths.jsonl"

BUKHARI_TOTAL=7563
MUSLIM_TOTAL=7470

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

clear

echo "🌙 Basirah - Hadith Download Monitor"
echo "====================================="
echo ""

while true; do
    # Get current counts
    BUKHARI_COUNT=$(wc -l < "$BUKHARI_FILE" 2>/dev/null || echo "0")
    MUSLIM_COUNT=$(wc -l < "$MUSLIM_FILE" 2>/dev/null || echo "0")

    # Calculate percentages
    BUKHARI_PCT=$((BUKHARI_COUNT * 100 / BUKHARI_TOTAL))
    MUSLIM_PCT=$((MUSLIM_COUNT * 100 / MUSLIM_TOTAL))
    TOTAL_PCT=$(((BUKHARI_COUNT + MUSLIM_COUNT) * 100 / (BUKHARI_TOTAL + MUSLIM_TOTAL)))

    # Calculate remaining
    BUKHARI_REM=$((BUKHARI_TOTAL - BUKHARI_COUNT))
    MUSLIM_REM=$((MUSLIM_TOTAL - MUSLIM_COUNT))
    TOTAL_REM=$((BUKHARI_REM + MUSLIM_REM))

    # Estimate time remaining (at ~2 sec per hadith with retries)
    SECONDS_REM=$((TOTAL_REM * 2))
    HOURS_REM=$((SECONDS_REM / 3600))
    MINUTES_REM=$(((SECONDS_REM % 3600) / 60))

    # Clear and redraw
    tput cup 3 0

    echo -e "${BLUE}Sahih al-Bukhari${NC}"
    echo -e "  Downloaded: ${GREEN}$BUKHARI_COUNT${NC} / $BUKHARI_TOTAL ($BUKHARI_PCT%)"
    echo -e "  Remaining:  ${YELLOW}$BUKHARI_REM${NC}"

    # Progress bar for Bukhari
    BAR_WIDTH=50
    FILLED=$((BUKHARI_PCT * BAR_WIDTH / 100))
    printf "  ["
    printf "%${FILLED}s" | tr ' ' '█'
    printf "%$((BAR_WIDTH - FILLED))s" | tr ' ' '░'
    printf "] %d%%\n" $BUKHARI_PCT
    echo ""

    echo -e "${BLUE}Sahih Muslim${NC}"
    echo -e "  Downloaded: ${GREEN}$MUSLIM_COUNT${NC} / $MUSLIM_TOTAL ($MUSLIM_PCT%)"
    echo -e "  Remaining:  ${YELLOW}$MUSLIM_REM${NC}"

    # Progress bar for Muslim
    FILLED=$((MUSLIM_PCT * BAR_WIDTH / 100))
    printf "  ["
    printf "%${FILLED}s" | tr ' ' '█'
    printf "%$((BAR_WIDTH - FILLED))s" | tr ' ' '░'
    printf "] %d%%\n" $MUSLIM_PCT
    echo ""

    echo -e "${BLUE}Total Progress${NC}"
    echo -e "  Downloaded: ${GREEN}$((BUKHARI_COUNT + MUSLIM_COUNT))${NC} / $((BUKHARI_TOTAL + MUSLIM_TOTAL)) ($TOTAL_PCT%)"
    echo -e "  Remaining:  ${YELLOW}$TOTAL_REM${NC} hadiths"
    echo ""

    # Progress bar for total
    FILLED=$((TOTAL_PCT * BAR_WIDTH / 100))
    printf "  ["
    printf "%${FILLED}s" | tr ' ' '█'
    printf "%$((BAR_WIDTH - FILLED))s" | tr ' ' '░'
    printf "] %d%%\n" $TOTAL_PCT
    echo ""

    if [ $TOTAL_REM -eq 0 ]; then
        echo -e "${GREEN}✅ Downloads complete!${NC}"
        echo ""
        echo "Next steps:"
        echo "  cd /home/syeddgx/Projects/Basirah/infra"
        echo "  ./complete-ingestion.sh"
        echo ""
        break
    else
        echo -e "Estimated time remaining: ${YELLOW}${HOURS_REM}h ${MINUTES_REM}m${NC}"
        echo ""
        echo "Press Ctrl+C to exit monitor (downloads continue in background)"
        echo ""

        # Show last log entries
        echo "Recent activity:"
        tail -n 2 "$PROJECT_ROOT/data/corpus/raw/bukhari/download_slow.log" 2>/dev/null | sed 's/^/  Bukhari: /'
        tail -n 2 "$PROJECT_ROOT/data/corpus/raw/muslim/download_slow.log" 2>/dev/null | sed 's/^/  Muslim:  /'
    fi

    sleep 5
done
