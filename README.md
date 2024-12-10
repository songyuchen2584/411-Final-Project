# Cocktail Maker Application

## Overview
The Cocktail Maker application is a web-based platform that manages user accounts and discovers cocktails. It allows users to create accounts, log in, and explore various cocktails. They can also retrieve random cocktail recipes, search for cocktails by name, and check if a specific drink is alcoholic or non-alcoholic.

The application is utilizes Flask, SQLAlchemy for database operations, and integrates with the CocktailDB API to fetch cocktail data. This README provides an overview of the application, including detailed descriptions of its routes.

**API Used:** https://www.thecocktaildb.com/api.php?ref=apilist.fun

## Routes and API Endpoints

### (1) Health Check
**Route:** /health
  - **Request Type:** GET
  - **Purpose:** This route serves as a health check endpoint to verify that the service is running and operational.
  - **Request Body:** None
  - **Response Format:** JSON
    - **Success Response Example:**

      StatusCode: 200

      Content: 

      {

        "status": "healthy"

      }
      
  - **Example Request:**
    {}
  - **Example Response:**

    {

      "status": "healthy"

    }

### (2) Create Account
**Route:** /create-account
  - **Request Type:** POST
  - **Purpose:** Creates a new user account
  - **Request Body:** 
    - username (String): User's chosen username.
    - password (String): User's chosen password.
  - **Response Format:** JSON
    - **Success Response Example:**

      StatusCode: 201

      Content: 

      {

        "message": "Account created successfully"

      }
  - **Example Request:**

      {

        "username": "newuser123",
        "password": "securepassword"

      }
  - **Example Response:**

    {

        "message": "Account created successfully",
        "status": "201"

    }

### (3) Login Account
**Route:** /login
  - **Request Type:** POST
  - **Purpose:** Authenticates a user by verifying their username and password.
  - **Request Body:** 
    - username (String): User's username.
    - password (String): User' password.
  - **Response Format:** JSON
    - **Success Response Example:**

      StatusCode: 200

      Content: 

      {

        "message": "Login successful"

      }
  - **Example Request:**

      {

        "username": "user123",
        "password": "mypassword"

      }
  - **Example Response:**

    {

        "message": "Login successful",
        "status": "200"

    }

### (4) Update Password
**Route:** /update-password
  - **Request Type:** POST
  - **Purpose:** Updates the password for an existing user account.
  - **Request Body:** 
    - username (String): The username of the user whose password is being updated.
    - password (String): The new password to be set for the user.
  - **Response Format:** JSON
    - **Success Response Example:**

      StatusCode: 200

      Content: 

      {

        "message": "Password updated successfully"

      }
  - **Example Request:**

      {

        "username": "user123",
        "new_password": "newsecurepassword"

      }
  - **Example Response:**

    {

        "message": "Password updated successfully",
        "status": "200"

    }

### (5) Fetch Random Drink
**Route:** /random-drink
  - **Request Type:** GET
  - **Purpose:** Fetches a random drink from the CocktailDB API.
  - **Request Body:** None
  - **Response Format:** JSON
    - **Success Response Example:**

      StatusCode: 200

      Content: 

      {

        "status": "success",
        "drink": {

          "id": 12345,
          "name": "Margarita",
          "category": "Cocktail",
          "alcoholic": "Alcoholic",
          "glass": "Cocktail Glass",
          "instructions": "Shake with ice and serve.",
          "ingredients": ["Tequila", "Lime Juice", "Triple Sec", null, null],
          "measures": ["2 oz", "1 oz", "1/2 oz", null, null],
          "thumbnail": "https://www.thecocktaildb.com/images/media/drink/5noda61589575158.jpg"

        }

      }
  - **Example Request:** None
  - **Example Response:**

    {

        "status": "success",
        "drink": {

          "id": 12345,
          "name": "Margarita",
          "category": "Cocktail",
          "alcoholic": "Alcoholic",
          "glass": "Cocktail Glass",
          "instructions": "Shake with ice and serve.",
          "ingredients": ["Tequila", "Lime Juice", "Triple Sec", null, null],
          "measures": ["2 oz", "1 oz", "1/2 oz", null, null],
          "thumbnail": "https://www.thecocktaildb.com/images/media/drink/5noda61589575158.jpg"

        }

    }

### (6) Fetch Drink by Name
**Route:** /drink/<string:drink_name>
  - **Request Type:** GET
  - **Purpose:** Fetches details of a drink by its name from the CocktailDB API.
  - **Request Body:** None
  - **Path Parameter:** 
    - drink_name (String): The name of the drink to fetch.
  - **Response Format:** JSON
    - **Success Response Example:**

      StatusCode: 200

      Content: 

      {
        
        "status": "success",
        "drink": {

          "id": 12345,
          "name": "Margarita",
          "category": "Cocktail",
          "alcoholic": "Alcoholic",
          "glass": "Cocktail Glass",
          "instructions": "Shake with ice and serve.",
          "ingredients": ["Tequila", "Lime Juice", "Triple Sec", null, null],
          "measures": ["2 oz", "1 oz", "1/2 oz", null, null],
          "thumbnail": "https://www.thecocktaildb.com/images/media/drink/5noda61589575158.jpg"

        }

      }
  - **Example Request:** /drink/Margarita
  - **Example Response:**

    {

        "status": "success",
        "drink": {

          "id": 12345,
          "name": "Margarita",
          "category": "Cocktail",
          "alcoholic": "Alcoholic",
          "glass": "Cocktail Glass",
          "instructions": "Shake with ice and serve.",
          "ingredients": ["Tequila", "Lime Juice", "Triple Sec", null, null],
          "measures": ["2 oz", "1 oz", "1/2 oz", null, null],
          "thumbnail": "https://www.thecocktaildb.com/images/media/drink/5noda61589575158.jpg"

        }

    }

### (7) Check if Drink is Alcoholic
**Route:** /drink/<string:drink_name>/alcoholic
  - **Request Type:** GET
  - **Purpose:** Checks if a drink is alcoholic based on its name using the CocktailDB API.
  - **Request Body:** None
  - **Path Parameter:** 
    - drink_name (String): The name of the drink to check.
  - **Response Format:** JSON
    - **Success Response Example:**

      StatusCode: 200

      Content: 

      {

        "status": "success"
        "is_alcoholic": true

      }
  - **Example Request:** /drink/Margarita/alcoholic
  - **Example Response:**

    {

        "status": "success",
        "is_alcoholic": true

    }