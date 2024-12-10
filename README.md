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

### (1) Create Account
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

