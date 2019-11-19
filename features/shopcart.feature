Feature: Shopcart store service back-end
    As a User
    I need a RESTful catalog service
    So that I can manage items in my shopcart

Background:
    Given the following shopcart
        | customer_id   | product_id    | text          | quantity  | price |
        | 1             | 1             | MacBook Pro   | 3         | 1000  |
        | 1             | 2             | iPhone        | 4         | 800   |
        | 2             | 3             | Apple Watch   | 1         | 400   |


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcart RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create
    When I visit the "Home Page"
    And I set the "Customer_ID" to "34"
    And I set the "Product_ID" to "23"
    And I set the "Text" to "Airpods"
    And I set the "Quantity" to "2"
    And I set the "Price" to "700"
    And I press the "Create" button
    Then I should see the message "Success"
    When I press the "Clear" button
    Then the "Customer_ID" field should be empty
    And the "Product_ID" field should be empty
    And the "Text" field should be empty
    And the "Quantity" field should be empty
    And the "Price" field should be empty
    When I set the "Customer_ID" to "34"
    And I set the "Product_ID" to "23"
    And I press the "Read" button
    Then I should see "Airpods" in the "Text" field
    And I should see "2" in the "Quantity" field
    And I should see "700" in the "Price" field
#Scenario: List 
    When I visit the "Home Page"
    And I set the "Customer_ID" to "2"
    And I press the "List" button
    Then I should see the message "List shopcart Success!"
    And I should see "2" in the results
    And I should see "3" in the results
    And I should see "Apple Watch" in the results
#Scenario: Query 
    When I visit the "Home Page"
    And I set the "Customer_ID" to "1"
    And I set the "Price" to "900"
    And I press the "Query" button
    Then I should see the message "Query shopcart Success!"
    And I should see "iPhone" in the results
    And I should see "800" in the results
    And I should not see "MacBook Pro" in the results
    And I should not see "Apple Watch" in the results
#Scenario: Read

Scenario: Delete
    When I visit the "Home Page"
    And I set the "Customer_ID" to "34"
    And I set the "Product_ID" to "23"
    And I press the "Delete" button
    Then I should see the message "Item has been Deleted!"
    When I press the "Clear" button
    Then the "Customer_ID" field should be empty
    And the "Product_ID" field should be empty
    And the "Text" field should be empty
    And the "Quantity" field should be empty
    And the "Price" field should be empty
    When I set the "Customer_ID" to "34"
    And I set the "Product_ID" to "23"
    And I press the "Read" button
    Then I should see the message "Read shopcart Failed"

#Scenario: Update 

Scenario: Action
    When I visit the "Home Page"
    And I set the "Customer_ID" to "2"
    And I set the "Product_ID" to "3"
    And I press the "Read" button
    Then I should see "Apple Watch" in the "Text" field
    And I should see "1" in the "Quantity" field
    And I should see "400" in the "Price" field
    When I press the "Order" button
    Then I should see the message "Product has been moved to Orders!"
