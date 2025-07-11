import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.utils.timezone import now
from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "stock")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order



class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass 

    updated_products = graphene.List(ProductType)
    success = graphene.String()

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated = []

        for product in low_stock_products:
            product.stock += 10 
            product.save()
            updated.append(product)

        return UpdateLowStockProducts(
            updated_products=updated,
            success=f"{len(updated)} product(s) updated successfully."
        )


class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists")
        if phone and not (phone.startswith('+') or '-' in phone):
            raise Exception("Invalid phone format")

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.JSONString)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created_customers = []
        errors = []

        for data in input:
            try:
                if Customer.objects.filter(email=data['email']).exists():
                    errors.append(f"Email {data['email']} already exists.")
                    continue
                customer = Customer(
                    name=data['name'],
                    email=data['email'],
                    phone=data.get('phone')
                )
                customer.full_clean()
                customer.save()
                created_customers.append(customer)
            except Exception as e:
                errors.append(f"{data['email']}: {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int(default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock):
        if price <= 0:
            raise Exception("Price must be positive.")
        if stock < 0:
            raise Exception("Stock cannot be negative.")

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.String()

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID.")

        if not product_ids:
            raise Exception("You must select at least one product.")

        products = []
        total = 0
        for pid in product_ids:
            try:
                product = Product.objects.get(pk=pid)
                products.append(product)
                total += float(product.price)
            except Product.DoesNotExist:
                raise Exception(f"Invalid product ID: {pid}")

        order = Order(customer=customer, total_amount=total, order_date=order_date or now())
        order.save()
        order.products.set(products)
        return CreateOrder(order=order)


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field() 


class Query(graphene.ObjectType):
    hello = graphene.String()
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter, order_by=graphene.List(of_type=graphene.String))
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter, order_by=graphene.List(of_type=graphene.String))
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter, order_by=graphene.List(of_type=graphene.String))

    def resolve_hello(self, info):
        return "Hello, GraphQL!"



schema = graphene.Schema(query=Query, mutation=Mutation)
