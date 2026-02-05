import os
import re
import subprocess
import xml.etree.ElementTree as ET

README_PATH = "README.md"
COVERAGE_XML = "coverage.xml"
REPORT_XML = "report.xml"

def run_tests():
    """Run pytest and generate XML reports."""
    print("Running tests...")
    # we use sys.executable to ensure we use the same python interpreter (inside venv)
    # assuming this script is run with the venv python
    cmd = ["pytest", f"--cov-report=xml:{COVERAGE_XML}", f"--junitxml={REPORT_XML}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode

def get_coverage_percentage():
    """Parse coverage.xml to get total coverage percentage."""
    if not os.path.exists(COVERAGE_XML):
        return 0
    tree = ET.parse(COVERAGE_XML)
    root = tree.getroot()
    # coverage.xml has a 'line-rate' attribute on the root <coverage> element
    line_rate = float(root.attrib.get("line-rate", 0))
    return int(line_rate * 100)

def get_test_status():
    """Parse report.xml to determine pass/fail status."""
    if not os.path.exists(REPORT_XML):
        return "unknown", "lightgrey"
    
    tree = ET.parse(REPORT_XML)
    root = tree.getroot()
    # <testsuite> usually has 'failures' and 'errors' attributes
    # But it might be the root or a child depending on pytest config.
    # JUnit XML root is usually <testsuites> or <testsuite>
    
    failures = 0
    errors = 0
    
    if root.tag == "testsuites":
        for suite in root:
            failures += int(suite.attrib.get("failures", 0))
            errors += int(suite.attrib.get("errors", 0))
    else:
        failures += int(root.attrib.get("failures", 0))
        errors += int(root.attrib.get("errors", 0))

    if failures + errors == 0:
        return "passing", "green"
    else:
        return "failing", "red"

def update_readme(coverage_pct, status, color):
    """Update README.md with new badges."""
    with open(README_PATH, "r") as f:
        content = f.read()

    # Shields.io URL construction
    # Tests Badge
    tests_badge = f"![Tests](https://img.shields.io/badge/tests-{status}-{color})"
    
    # Coverage Badge
    # Color logic for coverage
    cov_color = "red"
    if coverage_pct >= 90:
        cov_color = "brightgreen"
    elif coverage_pct >= 80:
        cov_color = "green"
    elif coverage_pct >= 70:
        cov_color = "yellow"
    elif coverage_pct >= 60:
        cov_color = "orange"
        
    cov_badge = f"![Coverage](https://img.shields.io/badge/coverage-{coverage_pct}%25-{cov_color})"

    # Badges Block
    badges_block = f"{tests_badge} {cov_badge}\n"

    # Regex to find existing badges line or insert at top
    # We look for a line starting with ![Tests] or containing shields.io badges
    badge_pattern = re.compile(r"^!\[Tests\].*img\.shields\.io.*$", re.MULTILINE)
    
    if badge_pattern.search(content):
        print("Updating existing badges...")
        new_content = badge_pattern.sub(badges_block.strip(), content)
    else:
        print("Inserting new badges at top...")
        # Insert after header if exists, or at very top
        header_match = re.search(r"^# .+\n", content)
        if header_match:
            # Insert after the first header line
            end_pos = header_match.end()
            new_content = content[:end_pos] + "\n" + badges_block + content[end_pos:]
        else:
            new_content = badges_block + "\n" + content

    with open(README_PATH, "w") as f:
        f.write(new_content)
    
    print(f"README.md updated with Status: {status}, Coverage: {coverage_pct}%")

def main():
    if not os.path.exists("scripts"):
        os.makedirs("scripts", exist_ok=True)
        
    run_tests()
    cov_pct = get_coverage_percentage()
    status, color = get_test_status()
    update_readme(cov_pct, status, color)

    # Cleanup (optional, keeping them might be useful for artifacts)
    # os.remove(COVERAGE_XML)
    # os.remove(REPORT_XML)

if __name__ == "__main__":
    main()
