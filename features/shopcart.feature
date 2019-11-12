Feature: Shopcart store service back-end
    As a User
    I need a RESTful catalog service
    So that I can manage items in my shopcart

Background:
    Given the following shopcart
        | customer id   | product id    | item text     | quantity  |
        | 1             | 1             | MacBook Pro   | 3         |
        | 1             | 2             | iPhone        | 4         |
        | 1             | 3             | Apple Watch   | 1         |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcart RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Item
    When I visit the "Home Page"
    And I set the "Customer ID" to "1"
    And I set the "Product ID" to "4"
    And I set the "Text" to "Coffee Machine"
    And I set the "Quantity" to "2"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Customer ID" field should be empty
    And the "Product ID" field should be empty
    And the "Text" field should be empty
    And the "Quantity" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see "1" in the "Customer ID" field
    And I should see "4" in the "Product ID" field
    And I should see "Coffee Machine" in the "Text" field
    And I should see "2" in the "Quantity" field

#Scenario: List
#Scenario: Query
#Scenario: Read
#Scenario: Delete
#Scenario: Update 
#Scenario: Action