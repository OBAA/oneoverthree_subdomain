from django.db import models


QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 26)]

# M = "{'M': 'quantity'}"
# FRIENDS = 'F'
# PUBLIC = 'P'
# CHOICES = (
#     (M, "M -- 175cm"),
#     (FRIENDS, "Friends"),
#     (PUBLIC, "Public"),
# )


SIZE_CHOICES = (
    ('S', 'S'),
    ('M', 'M'),
    ('L', 'L'),
    ('XL', 'XL'),
    ('36', '36'),
    ('37', '37'),
    ('38', '38'),
    ('39', '39'),
    ('40', '40'),
    ('41', '41'),
    ('42', '42'),
    ('43', '43'),
    ('44', '44'),
    ('45', '45'),
    ('46', '46'),
    ('W-28', 'W-28'),
    ('W-30', 'W-30'),
    ('W-32', 'W-32'),
    ('W-34', 'W-34'),
    ('W-36', 'W-36'),
    ('W-38', 'W-38'),
)


class Size(models.Model):
    size    = models.CharField(max_length=120, choices=SIZE_CHOICES, blank=True)
    stock   = models.PositiveIntegerField(null=True, choices=QUANTITY_CHOICES)

    def __str__(self):
        return str(self.size) + ": " + str(self.stock) + " in stock"



