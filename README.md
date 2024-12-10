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


