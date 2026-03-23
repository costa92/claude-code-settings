#!/bin/bash
##############################################################################
# Pre-Publish Verification Script
# Verifies that an article is ready for publication before moving to KB
# Fixes: bash variable naming issues, proper numeric comparisons
##############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ARTICLE_PATH="${1:-.}"
QUIET_MODE="${2:-false}"

# Check if file exists
if [ ! -f "$ARTICLE_PATH" ]; then
    echo -e "${RED}ERROR: Article file not found: $ARTICLE_PATH${NC}" >&2
    exit 1
fi

##############################################################################
# GATE 1: Placeholder Residue (BLOCKING)
##############################################################################
check_placeholders() {
    local placeholder_check

    # Use grep to check if placeholders exist (returns 0 if found, 1 if not)
    if grep -q '<!-- IMAGE:\|<!-- SCREENSHOT:' "$ARTICLE_PATH"; then
        # Placeholders found - this is a FAILURE
        echo -e "${RED}❌ FAIL: Unprocessed placeholders detected${NC}"
        echo ""
        echo "Found unprocessed placeholders:"
        grep -n '<!-- IMAGE:\|<!-- SCREENSHOT:' "$ARTICLE_PATH" | sed 's/^/  /'
        echo ""
        echo "Action: Re-run /article-craft:images to generate missing content."
        return 1
    else
        # No placeholders - this is a SUCCESS
        echo -e "${GREEN}✅ PASS: No unprocessed placeholders${NC}"
        return 0
    fi
}

##############################################################################
# GATE 2: Frontmatter Validation
##############################################################################
check_frontmatter() {
    local has_errors=false

    echo -e "\n--- Frontmatter Validation ---"

    for field in title date tags category status description; do
        if grep -q "^$field:" "$ARTICLE_PATH"; then
            echo -e "${GREEN}  ✅ $field${NC}"
        else
            echo -e "${YELLOW}  ❌ $field: MISSING${NC}"
            has_errors=true
        fi
    done

    if [ "$has_errors" = true ]; then
        echo ""
        echo "⚠️  WARNING: Some frontmatter fields are missing."
        return 2  # Return 2 for warning (non-blocking)
    else
        return 0
    fi
}

##############################################################################
# GATE 3: External Links (WeChat Compatibility)
##############################################################################
check_external_links() {
    echo -e "\n--- External Links Check ---"

    # Count bare URLs (not in code blocks or as markdown links)
    # This is a warning check, not blocking
    # Use grep with quiet mode to check presence
    if grep -q 'http://' "$ARTICLE_PATH"; then
        local url_count
        url_count=$(grep -c 'http://' "$ARTICLE_PATH")
        echo -e "${YELLOW}⚠️  WARNING: Found $url_count http:// URLs${NC}"
        echo "Ensure these are in proper Markdown format: [Name](URL)"
        return 2
    else
        echo -e "${GREEN}✅ PASS: No bare URLs found${NC}"
        return 0
    fi
}

##############################################################################
# GATE 4: No Mermaid Code Blocks
##############################################################################
check_mermaid() {
    echo -e "\n--- Mermaid Code Blocks Check ---"

    if grep -q '```mermaid' "$ARTICLE_PATH"; then
        echo -e "${YELLOW}⚠️  WARNING: Found Mermaid code blocks${NC}"
        echo "Replace with <!-- IMAGE --> placeholders for proper rendering"
        grep -n '```mermaid' "$ARTICLE_PATH" | sed 's/^/  /'
        return 2
    else
        echo -e "${GREEN}✅ PASS: No Mermaid code blocks${NC}"
        return 0
    fi
}

##############################################################################
# GATE 5: No Standalone Reference Section
##############################################################################
check_references() {
    echo -e "\n--- Reference Section Check ---"

    if grep -qE '^## (参考资料|参考链接|References)' "$ARTICLE_PATH"; then
        echo -e "${YELLOW}⚠️  WARNING: Found standalone reference section${NC}"
        echo "References should be inlined at mention point for WeChat compatibility"
        grep -n '^## (参考资料|参考链接|References)' "$ARTICLE_PATH" | sed 's/^/  /'
        return 2
    else
        echo -e "${GREEN}✅ PASS: No standalone reference section${NC}"
        return 0
    fi
}

##############################################################################
# Main verification flow
##############################################################################
main() {
    local blocking_error=false
    local has_warnings=false

    echo "=========================================="
    echo "Pre-Publish Verification"
    echo "File: $ARTICLE_PATH"
    echo "=========================================="

    # CRITICAL GATE 1: Check placeholders (blocking)
    echo -e "\n--- Unprocessed Placeholders (CRITICAL GATE) ---"
    if ! check_placeholders; then
        blocking_error=true
    fi

    # Non-blocking checks
    if check_frontmatter; then
        :
    else
        [ $? -eq 2 ] && has_warnings=true
    fi

    if check_external_links; then
        :
    else
        [ $? -eq 2 ] && has_warnings=true
    fi

    if check_mermaid; then
        :
    else
        [ $? -eq 2 ] && has_warnings=true
    fi

    if check_references; then
        :
    else
        [ $? -eq 2 ] && has_warnings=true
    fi

    # Final verdict
    echo ""
    echo "=========================================="

    if [ "$blocking_error" = true ]; then
        echo -e "${RED}RESULT: BLOCKED - Cannot publish${NC}"
        echo "Please fix the blocking error above and retry."
        echo "=========================================="
        exit 1
    elif [ "$has_warnings" = true ]; then
        echo -e "${YELLOW}RESULT: PASS (with warnings)${NC}"
        echo "Non-blocking issues found. Review suggestions above."
        echo "=========================================="
        exit 0
    else
        echo -e "${GREEN}RESULT: PASS - Ready for publication${NC}"
        echo "=========================================="
        exit 0
    fi
}

# Run main function
main "$@"
