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

#Scenario: Create 
#Scenario: List 
#Scenario: Query 
#Scenario: Read
#Scenario: Delete
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
