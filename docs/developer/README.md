# Development
========================

If you're new to Django, see [Getting Started with Django](https://www.djangoproject.com/start/) for an introduction to the framework.

## Local Setup

* Install Docker <https://docs.docker.com/get-docker/>
* Initialize the application:

  ```shell
  cd src
  docker-compose build
  ```
* Run the server: `docker-compose up`

  Press Ctrl-c when you'd like to exit or pass `-d` to run in detached mode.

Visit the running application at [http://localhost:8080](http://localhost:8080).

## Setting Vars

Non-secret environment variables for local development are set in [src/docker-compose.yml](../../src/docker-compose.yml).

Secrets (for example, if you'd like to have a working Login.gov authentication) go in `.env` in [src/](../../src/) with contents like this:

```
DJANGO_SECRET_LOGIN_KEY="<...>"
```

You'll need to create the `.env` file yourself. Get the secrets from Cloud.gov by running `cf env getgov-unstable`. More information is available in [rotate_application_secrets.md](../operations/runbooks/rotate_application_secrets.md).

## Viewing Logs

If you run via `docker-compose up`, you'll see the logs in your terminal.

If you run via `docker-compose up -d`, you can get logs with `docker-compose logs -f`.

You can change the logging verbosity, if needed. Do a web search for "django log level".

## Mock data

There is a `post_migrate` signal in [signals.py](../../src/registrar/signals.py) that will load the fixtures from [fixtures.py](../../src/registrar/fixtures.py), giving you some test data to play with while developing.

See the [database-access README](./database-access.md) for information on how to pull data to update these fixtures.

## Running tests

Crash course on Docker's `run` vs `exec`: in order to run the tests inside of a container, a container must be running. If you already have a container running, you can use `exec`. If you do not, you can use `run`, which will attempt to start one.

To get a container running:

```shell
cd src
docker-compose build
docker-compose up -d
```

Django's test suite:

```shell
docker-compose exec app ./manage.py test
```

OR

```shell
docker-compose exec app python -Wa ./manage.py test  # view deprecation warnings
```

Linters:

```shell
docker-compose exec app ./manage.py lint
```

### Testing behind logged in pages

To test behind logged in pages with external tools, like `pa11y-ci` or `OWASP Zap`, add

```
"registrar.tests.common.MockUserLogin"
```

to MIDDLEWARE in settings.py. **Remove it when you are finished testing.**

### Reducing console noise in tests

Some tests, particularly when using Django's test client, will print errors.

These errors do not indicate test failure, but can make the output hard to read.

To silence them, we have a helper function `less_console_noise`:

```python
from .common import less_console_noise
...
        with less_console_noise():
            # <test code goes here>
```

### Accessibility Scanning

The tool `pa11y-ci` is used to scan pages for compliance with a set of
accessibility rules. The scan runs as part of our CI setup (see
`.github/workflows/test.yaml`) but it can also be run locally. To run locally,
type

```shell
docker-compose run pa11y npm run pa11y-ci
```

The URLs that `pa11y-ci` will scan are configured in `src/.pa11yci`. When new
views and pages are added, their URLs should also be added to that file.

### Security Scanning

The tool OWASP Zap is used for scanning the codebase for compliance with
security rules. The scan runs as part of our CI setup (see
`.github/workflows/test.yaml`) but it can also be run locally. To run locally,
type

```shell
docker-compose run owasp
```

## USWDS and styling
We use the U.S. Web Design System (USWDS) for building and styling our applications. Additionally, we utilize the [uswds-compile tool](https://designsystem.digital.gov/documentation/getting-started/developers/phase-two-compile/) from USWDS  to compile and package the static assets.
When you run `docker-compose up` the `node` service in the container will begin to watch for changes in the `registrar/assets` folder, and will recompile once any changes are made.
Within the `registrar/assets` folder, the `_theme` folder contains three files initially generated by `uswds-compile`:
1. `_uswds-theme-custom-styles` contains all the custom styles created for this application
2. `_uswds-theme` contains all the custom theme settings (e.g. primary colors, fonts, banner color, etc..)
3. `styles.css` a entry point or index for the styles, forwards all of the other style files used in the project (i.e. the USWDS source code, the settings, and all custom stylesheets).

You can also compile the sass at any time using `npx gulp compile`. Similarly, you can copy over other static assets (images and javascript files), using `npx gulp copyAssets`.

## Nightly Builds

We run a deploy to staging from `main` nightly. You can see the deploys [here](https://github.com/cisagov/getgov/actions/workflows/deploy.yaml).

## Finite State Machines

In an effort to keep our domain logic centralized, we are representing the state of 
objects in the application using the [django-fsm](https://github.com/viewflow/django-fsm)
library. See the [ADR number 15](../architecture/decisions/0015-use-django-fs.md) for
more information on the topic.

## Login Time Bug

If you are seeing errors related to openid complaining about issuing a token from the future like this:

```
ERROR [djangooidc.oidc:243] Issued in the future
```

it may help to resync your laptop with time.nist.gov: 

```
sudo sntp -sS time.nist.gov
```
