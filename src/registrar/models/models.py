import re

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AbstractUser
from django.db import models

from django_fsm import FSMField, transition  # type: ignore


class User(AbstractUser):
    """
    A custom user model that performs identically to the default user model
    but can be customized later.
    """

    def __str__(self):
        try:
            return self.userprofile.display_name
        except ObjectDoesNotExist:
            return self.username


class TimeStampedModel(models.Model):
    """
    An abstract base model that provides self-updating
    `created_at` and `updated_at` fields.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        # don't put anything else here, it will be ignored


class AddressModel(models.Model):
    """
    An abstract base model that provides common fields
    for postal addresses.
    """

    # contact's street (null ok)
    street1 = models.TextField(blank=True)
    # contact's street (null ok)
    street2 = models.TextField(blank=True)
    # contact's street (null ok)
    street3 = models.TextField(blank=True)
    # contact's city
    city = models.TextField(blank=True)
    # contact's state or province (null ok)
    sp = models.TextField(blank=True)
    # contact's postal code (null ok)
    pc = models.TextField(blank=True)
    # contact's country code
    cc = models.TextField(blank=True)

    class Meta:
        abstract = True
        # don't put anything else here, it will be ignored


class ContactInfo(models.Model):
    """
    An abstract base model that provides common fields
    for contact information.
    """

    voice = models.TextField(blank=True)
    fax = models.TextField(blank=True)
    email = models.TextField(blank=True)

    class Meta:
        abstract = True
        # don't put anything else here, it will be ignored


class UserProfile(TimeStampedModel, ContactInfo, AddressModel):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    display_name = models.TextField()

    def __str__(self):
        if self.display_name:
            return self.display_name
        else:
            try:
                return self.user.username
            except ObjectDoesNotExist:
                return "No username"


class Website(models.Model):

    """Keep domain names in their own table so that applications can refer to
    many of them."""

    # domain names have strictly limited lengths, 255 characters is more than
    # enough.
    website = models.CharField(max_length=255, null=False, help_text="")

    # a domain name is alphanumeric or hyphen, up to 63 characters, doesn't
    # begin or end with a hyphen, followed by a TLD of 2-6 alphabetic characters
    DOMAIN_REGEX = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.[A-Za-z]{2,6}")

    @classmethod
    def string_could_be_domain(cls, domain: str) -> bool:
        """Return True if the string could be a domain name, otherwise False.

        TODO: when we have a Domain class, this could be a classmethod there.
        """
        if cls.DOMAIN_REGEX.match(domain):
            return True
        return False

    def could_be_domain(self) -> bool:
        """Could this instance be a domain?"""
        # short-circuit if self.website is null/None
        if not self.website:
            return False
        return self.string_could_be_domain(str(self.website))

    def __str__(self) -> str:
        return str(self.website)


class Contact(models.Model):

    """Contact information follows a similar pattern for each contact."""

    first_name = models.TextField(null=True, help_text="First name", db_index=True)
    middle_name = models.TextField(null=True, help_text="Middle name")
    last_name = models.TextField(null=True, help_text="Last name", db_index=True)
    title = models.TextField(null=True, help_text="Title")
    email = models.TextField(null=True, help_text="Email", db_index=True)
    phone = models.TextField(null=True, help_text="Phone", db_index=True)


class DomainApplication(TimeStampedModel):

    """A registrant's application for a new domain."""

    # #### Contants for choice fields ####
    STARTED = "started"
    SUBMITTED = "submitted"
    INVESTIGATING = "investigating"
    APPROVED = "approved"
    STATUS_CHOICES = [
        (STARTED, STARTED),
        (SUBMITTED, SUBMITTED),
        (INVESTIGATING, INVESTIGATING),
        (APPROVED, APPROVED),
    ]

    FEDERAL = "federal"
    INTERSTATE = "interstate"
    STATE_OR_TERRITORY = "state_or_territory"
    TRIBAL = "tribal"
    COUNTY = "county"
    CITY = "city"
    SPECIAL_DISTRICT = "special_district"
    ORGANIZATION_CHOICES = [
        (FEDERAL, "a federal agency"),
        (INTERSTATE, "an organization of two or more states"),
        (
            STATE_OR_TERRITORY,
            "one of the 50 U.S. states, the District of "
            "Columbia, American Samoa, Guam, Northern Mariana Islands, "
            "Puerto Rico, or the U.S. Virgin Islands",
        ),
        (
            TRIBAL,
            "a tribal government recognized by the federal or " "state government",
        ),
        (COUNTY, "a county, parish, or borough"),
        (CITY, "a city, town, township, village, etc."),
        (SPECIAL_DISTRICT, "an independent organization within a single state"),
    ]

    EXECUTIVE = "Executive"
    JUDICIAL = "Judicial"
    LEGISLATIVE = "Legislative"
    BRANCH_CHOICES = [(x, x) for x in (EXECUTIVE, JUDICIAL, LEGISLATIVE)]

    # #### Internal fields about the application #####
    status = FSMField(
        choices=STATUS_CHOICES,  # possible states as an array of constants
        default=STARTED,  # sensible default
        protected=False,  # can change state directly, particularly in Django admin
    )
    # This is the application user who created this application. The contact
    # information that they gave is in the `submitter` field
    creator = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="applications_created"
    )
    investigator = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="applications_investigating",
    )

    # ##### data fields from the initial form #####
    organization_type = models.CharField(
        max_length=255, choices=ORGANIZATION_CHOICES, help_text="Type of Organization"
    )

    federal_branch = models.CharField(
        max_length=50,
        choices=BRANCH_CHOICES,
        null=True,
        help_text="Branch of federal government",
    )

    is_election_office = models.BooleanField(
        null=True, help_text="Is your ogranization an election office?"
    )

    organization_name = models.TextField(
        null=True, help_text="Organization name", db_index=True
    )
    street_address = models.TextField(null=True, help_text="Street Address")
    unit_type = models.CharField(max_length=15, null=True, help_text="Unit type")
    unit_number = models.CharField(max_length=255, null=True, help_text="Unit number")
    state_territory = models.CharField(
        max_length=2, null=True, help_text="State/Territory"
    )
    zip_code = models.CharField(
        max_length=10, null=True, help_text="ZIP code", db_index=True
    )

    authorizing_official = models.ForeignKey(
        Contact,
        null=True,
        related_name="authorizing_official",
        on_delete=models.PROTECT,
    )

    # "+" means no reverse relation to lookup applications from Website
    current_websites = models.ManyToManyField(Website, related_name="current+")

    requested_domain = models.ForeignKey(
        Website,
        null=True,
        help_text="The requested domain",
        related_name="requested+",
        on_delete=models.PROTECT,
    )
    alternative_domains = models.ManyToManyField(Website, related_name="alternatives+")

    # This is the contact information provided by the applicant. The
    # application user who created it is in the `creator` field.
    submitter = models.ForeignKey(
        Contact,
        null=True,
        related_name="submitted_applications",
        on_delete=models.PROTECT,
    )

    purpose = models.TextField(null=True, help_text="Purpose of the domain")

    other_contacts = models.ManyToManyField(
        Contact, related_name="contact_applications"
    )

    security_email = models.CharField(
        max_length=320, null=True, help_text="Security email for public use"
    )

    anything_else = models.TextField(
        null=True, help_text="Anything else we should know?"
    )

    acknowledged_policy = models.BooleanField(
        null=True, help_text="Acknowledged .gov acceptable use policy"
    )

    @transition(field="status", source=STARTED, target=SUBMITTED)
    def submit(self):
        """Submit an application that is started."""

        # check our conditions here inside the `submit` method so that we
        # can raise more informative exceptions

        # requested_domain could be None here
        if (not self.requested_domain) or (not self.requested_domain.could_be_domain()):
            raise ValueError("Requested domain is not a legal domain name.")

        # if no exception was raised, then we don't need to do anything
        # inside this method, keep the `pass` here to remind us of that
        pass