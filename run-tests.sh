#!/bin/bash

echo "🧪 Gmail AI Organizer - Test Runner"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
COVERAGE=false
VERBOSE=false
BACKEND_ONLY=false
FRONTEND_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --backend|-b)
            BACKEND_ONLY=true
            shift
            ;;
        --frontend|-f)
            FRONTEND_ONLY=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./run-tests.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -c, --coverage     Run with coverage reports"
            echo "  -v, --verbose      Verbose output"
            echo "  -b, --backend      Run only backend tests"
            echo "  -f, --frontend     Run only frontend tests"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Track results
BACKEND_SUCCESS=0
FRONTEND_SUCCESS=0

# Backend Tests
if [ "$FRONTEND_ONLY" = false ]; then
    echo -e "${YELLOW}Running Backend Tests...${NC}"
    echo ""

    cd backend || exit 1

    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi

    # Build pytest command
    PYTEST_CMD="pytest"
    if [ "$COVERAGE" = true ]; then
        PYTEST_CMD="$PYTEST_CMD --cov=app --cov-report=html --cov-report=term-missing"
    fi
    if [ "$VERBOSE" = true ]; then
        PYTEST_CMD="$PYTEST_CMD -v"
    fi

    # Run tests
    $PYTEST_CMD
    BACKEND_SUCCESS=$?

    cd ..

    if [ $BACKEND_SUCCESS -eq 0 ]; then
        echo -e "${GREEN}✓ Backend tests passed${NC}"
    else
        echo -e "${RED}✗ Backend tests failed${NC}"
    fi
    echo ""
fi

# Frontend Tests
if [ "$BACKEND_ONLY" = false ]; then
    echo -e "${YELLOW}Running Frontend Tests...${NC}"
    echo ""

    cd frontend || exit 1

    # Build test command
    TEST_CMD="npm test --"
    if [ "$COVERAGE" = true ]; then
        TEST_CMD="npm run test:coverage --"
    fi

    # Run tests
    $TEST_CMD --run
    FRONTEND_SUCCESS=$?

    cd ..

    if [ $FRONTEND_SUCCESS -eq 0 ]; then
        echo -e "${GREEN}✓ Frontend tests passed${NC}"
    else
        echo -e "${RED}✗ Frontend tests failed${NC}"
    fi
    echo ""
fi

# Summary
echo "===================================="
echo "Test Summary"
echo "===================================="

if [ "$FRONTEND_ONLY" = false ]; then
    if [ $BACKEND_SUCCESS -eq 0 ]; then
        echo -e "Backend:  ${GREEN}PASSED${NC}"
    else
        echo -e "Backend:  ${RED}FAILED${NC}"
    fi
fi

if [ "$BACKEND_ONLY" = false ]; then
    if [ $FRONTEND_SUCCESS -eq 0 ]; then
        echo -e "Frontend: ${GREEN}PASSED${NC}"
    else
        echo -e "Frontend: ${RED}FAILED${NC}"
    fi
fi

echo ""

# Coverage reports
if [ "$COVERAGE" = true ]; then
    echo "Coverage reports generated:"
    if [ "$FRONTEND_ONLY" = false ]; then
        echo "  Backend:  backend/htmlcov/index.html"
    fi
    if [ "$BACKEND_ONLY" = false ]; then
        echo "  Frontend: frontend/coverage/index.html"
    fi
    echo ""
fi

# Exit with appropriate code
if [ "$FRONTEND_ONLY" = false ] && [ "$BACKEND_ONLY" = false ]; then
    if [ $BACKEND_SUCCESS -eq 0 ] && [ $FRONTEND_SUCCESS -eq 0 ]; then
        echo -e "${GREEN}All tests passed! 🎉${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed ❌${NC}"
        exit 1
    fi
elif [ "$BACKEND_ONLY" = true ]; then
    exit $BACKEND_SUCCESS
else
    exit $FRONTEND_SUCCESS
fi
