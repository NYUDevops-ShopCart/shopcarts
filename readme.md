### NYU-DevOps Shopcart Squad

README for the shopcart squad.

#### API calls
URL | Operation | Description
-- | -- | --
`GET /shopcarts/<int:customer_id>` | READ | Returns list of all of the shop cart items
`GET /shopcarts/query/<int:customer_id>` | READ | Returns items of the shop cart items that are below the target price
`GET /shopcarts/<int:customer_id>/<int:product_id>` | READ | Retrieve a single shop cart item
`POST /shopcarts/<int:customer_id>` | CREATE | Creates a new item entry for the cart
`PUT /shopcarts/<int:customer_id>/<int:product_id>` | UPDATE | Update particular item quantity
`DELETE /shopcarts/<int:customer_id>/<int:product_id>` | DELETE | Delete particular shopcart item
`PUT /shopcarts/checkout/<int:customer_id>/<int:product_id>` | UPDATE | Move the shop cart item to order

#### Run and Test
- Clone the repository using: `git clone https://github.com/NYUDevops-ShopCart/shopcarts.git`
- Start the Vagrant VM using : `vagrant up`
- After the VM has been provisioned ssh into it using: `vagrant ssh`
- cd into `/vagrant` using `cd /vagrant` and set init file path by using export FLASK_APP=service/__init__.py 
- start the server using `flask run --host=0.0.0.0`
- for testing use nosetests
