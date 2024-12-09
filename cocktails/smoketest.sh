#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health checks
#
###############################################

check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

##############################################
#
# User Management
#
##############################################

create_user() {
  echo "Creating a new user..."
  curl -s -X POST "$BASE_URL/create-account" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}' | grep -q '"message": "Account created successfully"'
  if [ $? -eq 0 ]; then
    echo "User created successfully."
  else
    echo "Failed to create user."
    exit 1
  fi
}

login_user() {
  echo "Logging in user..."
  response=$(curl -s -X POST "$BASE_URL/login" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}')
  if echo "$response" | grep -q '"message": "Login successful"'; then
    echo "User logged in successfully."
    [ "$ECHO_JSON" = true ] && echo "$response" | jq .
  else
    echo "Failed to log in user."
    [ "$ECHO_JSON" = true ] && echo "$response" | jq .
    exit 1
  fi
}

update_password() {
  echo "Updating user password..."
  curl -s -X POST "$BASE_URL/update-password" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "new_password":"newpassword123"}' | grep -q '"message": "Password updated successfully"'
  if [ $? -eq 0 ]; then
    echo "Password updated successfully."
  else
    echo "Failed to update password."
    exit 1
  fi
}

##############################################
#
# Drinks
#
##############################################

get_random_drink() {
  echo "Fetching a random drink..."
  response=$(curl -s -X GET "$BASE_URL/random-drink")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Random drink fetched successfully."
    [ "$ECHO_JSON" = true ] && echo "$response" | jq .
  else
    echo "Failed to fetch random drink."
    [ "$ECHO_JSON" = true ] && echo "$response" | jq .
    exit 1
  fi
}

fetch_drink_by_name() {
  echo "Fetching a drink by name (Margarita)..."
  response=$(curl -s -X GET "$BASE_URL/drink/Margarita")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Drink fetched successfully by name."
    [ "$ECHO_JSON" = true ] && echo "$response" | jq .
  else
    echo "Failed to fetch drink by name."
    [ "$ECHO_JSON" = true ] && echo "$response" | jq .
    exit 1
  fi
}

check_drink_alcoholic() {
  echo "Checking if drink is alcoholic (Absolutely Cranberry Smash)..."
  curl -X GET "$BASE_URL/drink/Absolutely Cranberry Smash/alcoholic"
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Alcoholic status fetched successfully."
    [ "$ECHO_JSON" = true ] && echo "$response" | jq .
  else
    echo "Failed to fetch alcoholic status."
    [ "$ECHO_JSON" = true ] && echo "$response" | jq .
    exit 1
  fi
}

##############################################
#
# Drink List Management
#
##############################################

add_drink() {
  echo "Adding a drink to the list (Margarita)..."
  curl -s -X POST "$BASE_URL/create-drink" -H "Content-Type: application/json" \
    -d '{"name":"Margarita"}' | grep -q '"status": "Drink added"'
  if [ $? -eq 0 ]; then
    echo "Drink added successfully."
  else
    echo "Failed to add drink."
    exit 1
  fi
}

remove_drink() {
  echo "Removing a drink from the list (Margarita)..."
  curl -s -X POST "$BASE_URL/remove-drink" -H "Content-Type: application/json" \
    -d '{"name":"Margarita"}' | grep -q '"status": "Drink removed"'
  if [ $? -eq 0 ]; then
    echo "Drink removed successfully."
  else
    echo "Failed to remove drink."
    exit 1
  fi
}

list_drinks() {
  echo "Listing drinks in alphabetical order..."
  response=$(curl -s -X GET "$BASE_URL/list-drinks")
  if [ $? -eq 0 ]; then
    echo "Drinks listed successfully."
    [ "$ECHO_JSON" = true ] && echo "$response" | jq .
  else
    echo "Failed to list drinks."
    exit 1
  fi
}

##############################################
#
# Initialize Database
#
##############################################

init_db() {
  echo "Initializing the database..."
  response=$(curl -s -X POST "$BASE_URL/init-db")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Database initialized successfully."
    [ "$ECHO_JSON" = true ] && echo "$response" | jq .
  else
    echo "Failed to initialize database."
    exit 1
  fi
}

##############################################
#
# Execute Tests
#
##############################################

check_health
init_db
create_user
login_user
update_password
get_random_drink
fetch_drink_by_name
check_drink_alcoholic
add_drink
list_drinks
remove_drink

echo "All tests passed successfully!"
