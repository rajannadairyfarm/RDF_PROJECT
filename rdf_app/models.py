


from cloudinary import CloudinaryImage
from django.utils.text import slugify


def generate_unique_slug(model_class, value, instance=None):
    """
    Generate a unique SEO-friendly slug.

    Example:
        fresh-milk
        fresh-milk-2
        fresh-milk-3
    """

    base_slug = slugify(value)

    if not base_slug:
        base_slug = "item"

    slug = base_slug
    counter = 2

    queryset = model_class.objects.all()

    if instance and instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    while queryset.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug



def generate_seo_description(*sources, max_length=320):
    """
    Build a clean SEO description from available content.
    """

    for source in sources:

        if not source:
            continue

        text = " ".join(str(source).split()).strip()

        if not text:
            continue

        if len(text) <= max_length:
            return text

        truncated = text[:max_length]

        if " " in truncated:
            truncated = truncated.rsplit(" ", 1)[0]

        return truncated.rstrip(".,;:-") + "..."

    return ""




import uuid

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from cloudinary.models import CloudinaryField


class UserManager(BaseUserManager):
    """
    Custom manager for the User model.
    """

    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email address is required.")

        if not full_name:
            raise ValueError("Full name is required.")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            full_name=full_name.strip(),
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email,
        full_name,
        password=None,
        **extra_fields
    ):
        """
        Creates an admin/staff account.

        This project intentionally does not use
        Django's is_superuser field.
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff=True."
            )

        return self.create_user(
            email=email,
            full_name=full_name,
            password=password,
            **extra_fields
        )


class User(AbstractBaseUser):

    user_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True
    )

    full_name = models.CharField(
        max_length=150
    )

    email = models.EmailField(
        unique=True,
        db_index=True
    )

    phone = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True
    )

    address = models.TextField(
        null=True,
        blank=True
    )

    image = CloudinaryField(
        "image",
        blank=True,
        null=True,
        asset_folder="rdf/users",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    date_joined = models.DateTimeField(
        auto_now_add=True
    )

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "full_name"
    ]

    class Meta:
        db_table = "users"
        ordering = ["-date_joined"]

    def save(self, *args, **kwargs):

        if not self.user_id:
            self.user_id = (
                f"RDFUSR-{uuid.uuid4().hex[:8].upper()}"
            )

        if self.email:
            self.email = self.email.lower().strip()

        if self.full_name:
            self.full_name = self.full_name.strip()

        super().save(*args, **kwargs)

    # ==========================================================
    # DJANGO ADMIN / PERMISSION SUPPORT
    # ==========================================================

    def get_user_permissions(self, obj=None):
        """
        Return permissions directly assigned to this user.

        The current RDF project does not use Django's
        permission-assignment system.
        """
        return set()

    def get_group_permissions(self, obj=None):
        """
        Return permissions inherited from groups.

        The current RDF project does not use Django groups.
        """
        return set()

    def get_all_permissions(self, obj=None):
        """
        Return all permissions available to this user.

        Staff users are allowed to access Django Admin.
        Normal customers have no admin permissions.
        """

        if not self.is_active or not self.is_staff:
            return set()

        return {
            "admin.access",
        }

    def has_perm(self, perm, obj=None):
        """
        Return True if the user has the specified permission.

        RDF currently uses is_staff as the admin-access
        control.
        """

        return self.is_active and self.is_staff

    def has_module_perms(self, app_label):
        """
        Return True if the user can access an application's
        models inside Django Admin.
        """

        return self.is_active and self.is_staff

    def __str__(self):
        return f"{self.user_id} - {self.full_name}"









import uuid

from django.db import models
from django.utils import timezone
from django.conf import settings


class EmailVerificationToken(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_verification_tokens"
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField()

    is_used = models.BooleanField(
        default=False
    )

    class Meta:
        db_table = "email_verification_tokens"
        ordering = ["-created_at"]

    def is_valid(self):
        return (
            not self.is_used
            and timezone.now() < self.expires_at
        )

    def __str__(self):
        return f"{self.user.email} - {self.token}"
    



class PasswordResetToken(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens"
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField()

    is_used = models.BooleanField(
        default=False
    )

    def is_valid(self):
        return (
            not self.is_used
            and timezone.now() < self.expires_at
        )

    class Meta:
        db_table = "password_reset_tokens"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.token}"
    
    
    
    
from django.core.validators import RegexValidator
    
class UserProfile(models.Model):

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
        ("prefer_not_to_say", "Prefer not to say"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=30,
        choices=GENDER_CHOICES,
        blank=True,
        default=""
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    state = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    pincode = models.CharField(
        max_length=10,
        blank=True,
        default="",
        validators=[
            RegexValidator(
                regex=r"^[0-9]{4,10}$",
                message="Enter a valid pincode."
            )
        ]
    )

    alternate_phone = models.CharField(
        max_length=15,
        blank=True,
        default=""
    )

    bio = models.TextField(
        max_length=500,
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "user_profiles"

    def __str__(self):
        return f"Profile - {self.user.email}"
    
    
    def completion_percentage(self):
        fields = [
            bool(self.user.full_name),
            bool(self.user.email),
            bool(self.user.phone),
            bool(self.user.image),
            bool(self.user.address),
            bool(self.city),
            bool(self.state),
            bool(self.pincode),
            bool(self.date_of_birth),
            bool(self.gender),
            bool(self.bio),
        ]

        completed = sum(fields)
        total = len(fields)

        if total == 0:
            return 0

        return round((completed / total) * 100)


    def missing_fields(self):
        missing = []

        if not self.user.full_name:
            missing.append("Full name")

        if not self.user.email:
            missing.append("Email")

        if not self.user.phone:
            missing.append("Phone number")

        if not self.user.image:
            missing.append("Profile photo")

        if not self.user.address:
            missing.append("Address")

        if not self.city:
            missing.append("City")

        if not self.state:
            missing.append("State")

        if not self.pincode:
            missing.append("Pincode")

        if not self.date_of_birth:
            missing.append("Date of birth")

        if not self.gender:
            missing.append("Gender")

        if not self.bio:
            missing.append("Bio")

        return missing
    

from django.db import models
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError

class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        db_index=True
    )

    description = models.TextField(
        max_length=500,
        blank=True,
        default=""
    )

    image = CloudinaryField(
        "category_image",
        blank=True,
        null=True,
        asset_folder="rdf/categories",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True
    )

    is_featured = models.BooleanField(
        default=False,
        db_index=True
    )

    seo_title = models.CharField(
        max_length=160,
        blank=True,
        default=""
    )

    seo_description = models.CharField(
        max_length=320,
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "categories"
        ordering = ["name"]

        indexes = [
            models.Index(
                fields=["is_active", "name"]
            ),
            models.Index(
                fields=["is_featured", "is_active"]
            ),
        ]
        
    
    def save(self, *args, **kwargs):

        self.name = self.name.strip()

        if not self.slug:
            self.slug = generate_unique_slug(
                Category,
                self.name,
                self
            )

        if not self.seo_title:
            self.seo_title = (
                f"{self.name} | Rajanna Dairy Farm"
            )
            
            
        if not self.seo_description:
            self.seo_description = generate_seo_description(
                self.description
            )
        super().save(*args, **kwargs)
    
    def clean(self):

        errors = {}

        if self.seo_title:

            seo_title = self.seo_title.strip()

            if len(seo_title) < 20:
                errors["seo_title"] = (
                    "SEO title is too short. "
                    "Use a descriptive title."
                )

            elif len(seo_title) > 70:
                errors["seo_title"] = (
                    "SEO title is too long. "
                    "Keep it around 50–60 characters."
                )

        if self.seo_description:

            seo_description = self.seo_description.strip()

            if len(seo_description) < 50:
                errors["seo_description"] = (
                    "SEO description is too short. "
                    "Provide useful information about this category."
                )

            elif len(seo_description) > 170:
                errors["seo_description"] = (
                    "SEO description is too long. "
                    "Keep it around 140–160 characters."
                )

        if errors:
            raise ValidationError(errors)
        
    

    def __str__(self):
        return self.name
    
    
    











import uuid
from decimal import Decimal

from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models
from django.utils.text import slugify

from cloudinary.models import CloudinaryField


class Product(models.Model):

    UNIT_CHOICES = [
        ("kg", "Kilogram"),
        ("g", "Gram"),
        ("l", "Litre"),
        ("ml", "Millilitre"),
        ("piece", "Piece"),
        ("pack", "Pack"),
        ("box", "Box"),
    ]

    product_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    name = models.CharField(
        max_length=200,
        db_index=True
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        db_index=True
    )

    sku = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        db_index=True
    )

    short_description = models.CharField(
        max_length=300,
        blank=True,
        default=""
    )

    description = models.TextField(
        blank=True,
        default=""
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ]
    )

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default="piece"
    )

    stock_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    low_stock_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("5.00"),
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    main_image = CloudinaryField(
        "product_image",
        blank=True,
        null=True,
        asset_folder="rdf/products"
    )

    is_in_stock = models.BooleanField(
        default=False,
        db_index=True
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True
    )

    is_featured = models.BooleanField(
        default=False,
        db_index=True
    )

    seo_title = models.CharField(
        max_length=160,
        blank=True,
        default="",
        editable=False,
    )

    seo_description = models.CharField(
        max_length=320,
        blank=True,
        default="",
        editable=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "products"

        ordering = [
            "-created_at"
        ]

        indexes = [
            models.Index(
                fields=[
                    "is_active",
                    "category"
                ]
            ),
            models.Index(
                fields=[
                    "is_active",
                    "is_in_stock"
                ]
            ),
            models.Index(
                fields=[
                    "is_featured",
                    "is_active"
                ]
            ),
            models.Index(
                fields=[
                    "category",
                    "name"
                ]
            ),
        ]

    def save(self, *args, **kwargs):

        # Generate unique product ID
        if not self.product_id:
            self.product_id = (
                f"RDFPRD-{uuid.uuid4().hex[:8].upper()}"
            )

        # Normalize product data
        self.name = self.name.strip()
        # self.sku = self.sku.strip().upper()
        
        if not self.sku:
            self.sku = self.generate_sku()
        
        if not self.slug:
            self.slug = generate_unique_slug(
                Product,
                self.name,
                self
            )

        # if not self.seo_title:
        #     self.seo_title = (
        #         f"{self.name} | Rajanna Dairy Farm"
        #     )
            
        
        # if not self.seo_description:
        #     self.seo_description = generate_seo_description(
        #         self.short_description,
        #         self.description
        #     )
        
        # -------------------------------------------------
        # Automatic SEO
        # -------------------------------------------------

        self.seo_title = (
            f"{self.name} | Rajanna Dairy Farm"
        )[:70]

        seo_base = (
            f"Buy fresh {self.name} from Rajanna Dairy Farm. "
            f"{self.short_description or self.description}"
        )

        seo_base = " ".join(seo_base.split()).strip()

        if len(seo_base) < 50:
            seo_base = (
                f"Buy fresh and quality {self.name} "
                f"from Rajanna Dairy Farm. "
                f"Fresh dairy products delivered with care."
            )

        self.seo_description = seo_base[:170].rstrip()
        discount = (
            self.price
            * self.discount_percentage
            / Decimal("100")
        )

        self.selling_price = (
            self.price - discount
        ).quantize(
            Decimal("0.01")
        )

        # Automatically determine stock status
        self.is_in_stock = (
            self.stock_quantity > Decimal("0.00")
        )

        super().save(*args, **kwargs)
            
    def clean(self):
        """
        Validate only user-editable product data.

        SEO fields are generated automatically and therefore
        are not validated as admin form inputs.
        """
        errors = {}

        if self.name:
            self.name = self.name.strip()

        if self.price is not None and self.price < Decimal("0.00"):
            errors["price"] = "Price cannot be negative."

        if self.discount_percentage is not None:
            if not (
                Decimal("0.00")
                <= self.discount_percentage
                <= Decimal("100.00")
            ):
                errors["discount_percentage"] = (
                    "Discount percentage must be between 0 and 100."
                )

        if errors:
            raise ValidationError(errors)
    
    def get_image_url(self, width=800, height=800):

        if not self.main_image:
            return ""

        image = CloudinaryImage(
            self.main_image.public_id
        )

        return image.build_url(
            transformation=[
                {
                    "width": width,
                    "height": height,
                    "crop": "fill",
                    "gravity": "auto",
                    "quality": "auto",
                    "fetch_format": "auto",
                }
            ]
        )
        
    def generate_sku(self):
        category_code = slugify(self.category.name).replace("-", "").upper()[:8]

        prefix = f"RDF-{category_code}"

        last_product = (
            Product.objects
            .filter(sku__startswith=f"{prefix}-")
            .order_by("-id")
            .first()
        )

        if last_product and last_product.sku:
            try:
                last_number = int(last_product.sku.rsplit("-", 1)[-1])
            except ValueError:
                last_number = 0
        else:
            last_number = 0

        return f"{prefix}-{last_number + 1:03d}"


    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    
    



class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "carts"

    def __str__(self):
        return f"Cart - {self.user}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        total = Decimal("0.00")

        for item in self.items.select_related("product"):
            total += item.item_total

        return total.quantize(Decimal("0.01"))
    
    



class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="cart_items"
    )

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cart_items"

        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_cart_product"
            )
        ]

        indexes = [
            models.Index(
                fields=["cart", "product"],
                name="cartitem_cart_product_idx"
            ),
        ]

    def __str__(self):
        return f"{self.cart} - {self.product.name}"

    @property
    def item_total(self):
        return (
            self.product.selling_price * self.quantity
        ).quantize(Decimal("0.01"))
        
        




class Address(models.Model):

    ADDRESS_TYPE_CHOICES = [
        ("home", "Home"),
        ("work", "Work"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses"
    )

    full_name = models.CharField(
        max_length=150
    )

    phone_number = models.CharField(
        max_length=15
    )

    address_line1 = models.CharField(
        max_length=255
    )

    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    landmark = models.CharField(
        max_length=150,
        blank=True,
        default=""
    )

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    pincode = models.CharField(
        max_length=10
    )

    address_type = models.CharField(
        max_length=20,
        choices=ADDRESS_TYPE_CHOICES,
        default="home"
    )

    is_default = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "addresses"
        ordering = ["-is_default", "-created_at"]

        indexes = [
            models.Index(
                fields=["user", "is_default"],
                name="address_user_default_idx"
            ),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.city}"
    
    
    



class Order(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("razorpay", "Razorpay"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders"
    )

    order_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        db_index=True
    )

    # Address snapshot
    full_name = models.CharField(
        max_length=150
    )

    phone_number = models.CharField(
        max_length=15
    )

    address_line1 = models.CharField(
        max_length=255
    )

    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    landmark = models.CharField(
        max_length=150,
        blank=True,
        default=""
    )

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    pincode = models.CharField(
        max_length=10
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    delivery_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="cod"
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending"
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "orders"

        ordering = [
            "-created_at"
        ]

        indexes = [
            models.Index(
                fields=["user", "-created_at"],
                name="order_user_created_idx"
            ),
            models.Index(
                fields=["status", "-created_at"],
                name="order_status_created_idx"
            ),
        ]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):

        if not self.order_number:
            import uuid

            self.order_number = (
                f"RDFORD-{uuid.uuid4().hex[:12].upper()}"
            )

        super().save(*args, **kwargs)
        
        
        
        



class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items"
    )

    # Snapshot fields
    product_name = models.CharField(
        max_length=200
    )

    sku = models.CharField(
        max_length=50
    )

    unit = models.CharField(
        max_length=20
    )

    quantity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1)
        ]
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00"))
        ]
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "order_items"

        indexes = [
            models.Index(
                fields=["order"],
                name="orderitem_order_idx"
            ),
            models.Index(
                fields=["product"],
                name="orderitem_product_idx"
            ),
        ]

    def __str__(self):
        return (
            f"{self.product_name} "
            f"x {self.quantity}"
        )
        
        


class Subscriber(models.Model):
    email = models.EmailField(
        max_length=254,
        unique=True,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "subscribers"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email
    
    
    























from django.utils import timezone
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

class MilkSubscription(models.Model):

    STATUS_CHOICES = [
    ("pending", "Pending"),
    ("active", "Active"),
    ("paused", "Paused"),
    ("cancelled", "Cancelled"),
    ("expired", "Expired"),
]

    BILLING_CYCLE_CHOICES = [
        ("monthly", "Monthly"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="milk_subscriptions",
    )

    address = models.ForeignKey(
        "Address",
        on_delete=models.PROTECT,
        related_name="milk_subscriptions",
    )

    subscription_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        db_index=True,
    )

    start_date = models.DateField()

    end_date = models.DateField(
        blank=True,
        null=True,
    )

    billing_cycle = models.CharField(
        max_length=20,
        choices=BILLING_CYCLE_CHOICES,
        default="monthly",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        db_index=True,
    )

    notes = models.TextField(
        blank=True,
        default="",
        max_length=500,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "milk_subscriptions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["user", "status"],
                name="milk_sub_user_status_idx",
            ),
            models.Index(
                fields=["status", "start_date"],
                name="milk_sub_status_start_idx",
            ),
        ]

    def __str__(self):
        return self.subscription_number

    def save(self, *args, **kwargs):
        if not self.subscription_number:
            import uuid

            self.subscription_number = (
                f"RDFSUB-{uuid.uuid4().hex[:12].upper()}"
            )

        super().save(*args, **kwargs)


class MilkSubscriptionItem(models.Model):

    FREQUENCY_CHOICES = [
        ("daily", "Daily"),
    ]

    subscription = models.ForeignKey(
        MilkSubscription,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "Product",
        on_delete=models.PROTECT,
        related_name="milk_subscription_items",
    )

    quantity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
        ]
    )

    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )

    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default="daily",
    )

    start_date = models.DateField()

    end_date = models.DateField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "milk_subscription_items"
        ordering = ["id"]
        indexes = [
            models.Index(
                fields=["subscription"],
                name="milk_sub_item_sub_idx",
            ),
            models.Index(
                fields=["product"],
                name="milk_sub_item_product_idx",
            ),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.subscription.subscription_number}"

    @property
    def daily_amount(self):
        return (
            self.price_per_unit * self.quantity
        ).quantize(Decimal("0.01"))


class MilkDelivery(models.Model):

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("delivered", "Delivered"),
        ("skipped", "Skipped"),
        ("missed", "Missed"),
        ("paused", "Paused"),
        ("cancelled", "Cancelled"),
    ]

    subscription = models.ForeignKey(
        MilkSubscription,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )

    subscription_item = models.ForeignKey(
        MilkSubscriptionItem,
        on_delete=models.PROTECT,
        related_name="deliveries",
    )

    delivery_date = models.DateField(
        db_index=True,
    )

    quantity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
        ]
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="scheduled",
        db_index=True,
    )

    delivered_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    notes = models.CharField(
        max_length=300,
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "milk_deliveries"
        ordering = ["-delivery_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "subscription_item",
                    "delivery_date",
                ],
                name="unique_milk_delivery_day",
            )
        ]
        indexes = [
            models.Index(
                fields=["subscription", "delivery_date"],
                name="milk_delivery_sub_date_idx",
            ),
            models.Index(
                fields=["delivery_date", "status"],
                name="milk_delivery_date_status_idx",
            ),
        ]
    
    def save(self, *args, **kwargs):
        self.total_amount = (
            self.unit_price * self.quantity
        ).quantize(Decimal("0.01"))

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.subscription.subscription_number} - "
            f"{self.delivery_date}"
        )


class MilkBill(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("partial", "Partially Paid"),
        ("paid", "Paid"),
    ]

    subscription = models.ForeignKey(
        MilkSubscription,
        on_delete=models.PROTECT,
        related_name="bills",
    )

    billing_month = models.PositiveSmallIntegerField()

    billing_year = models.PositiveSmallIntegerField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
        default=Decimal("0.00"),
    )

    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
        default=Decimal("0.00"),
    )

    pending_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
        default=Decimal("0.00"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
    )

    payment_date = models.DateField(
        blank=True,
        null=True,
    )
    email_sent = models.BooleanField(
    default=False,
    )

    email_sent_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    notes = models.CharField(
        max_length=500,
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "milk_bills"
        ordering = ["-billing_year", "-billing_month"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "subscription",
                    "billing_month",
                    "billing_year",
                ],
                name="unique_milk_bill_month",
            )
        ]
        indexes = [
            models.Index(
                fields=[
                    "subscription",
                    "billing_year",
                    "billing_month",
                ],
                name="milk_bill_sub_period_idx",
            ),
            models.Index(
                fields=["status", "-created_at"],
                name="milk_bill_status_created_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.subscription.subscription_number} - "
            f"{self.billing_month}/{self.billing_year}"
        )

    def save(self, *args, **kwargs):
        self.pending_amount = max(
            Decimal("0.00"),
            self.total_amount - self.paid_amount,
        )

        if self.paid_amount <= Decimal("0.00"):
            self.status = "pending"
        elif self.paid_amount < self.total_amount:
            self.status = "partial"
        else:
            self.status = "paid"
            self.payment_date = self.payment_date or timezone.localdate()

        super().save(*args, **kwargs)