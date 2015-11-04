from django.core.management import CommandError, BaseCommand, get_commands, load_command_class


def call_command(name, *args, **options):
    """
    Calls the given command, with the given options and args/kwargs.

    This is the primary API you should use for calling specific commands.

    Some examples:
        call_command('migrate')
        call_command('shell', plain=True)
        call_command('sqlmigrate', 'myapp')

    Copy of the function from django.core.management. In addition to the
    standard functionality, stores the raw args on the command instance.
    """
    # Load the command object.
    try:
        app_name = get_commands()[name]
    except KeyError:
        raise CommandError("Unknown command: %r" % name)

    if isinstance(app_name, BaseCommand):
        # If the command is already loaded, use it directly.
        command = app_name
    else:
        command = load_command_class(app_name, name)

    # Store the raw args on the command so they can be used later if needed
    command.raw_args = args

    # Simulate argument parsing to get the option defaults (see #10080 for details).
    parser = command.create_parser('', name)
    if command.use_argparse:
        # Use the `dest` option name from the parser option
        opt_mapping = {sorted(s_opt.option_strings)[0].lstrip('-').replace('-', '_'): s_opt.dest
                       for s_opt in parser._actions if s_opt.option_strings}
        arg_options = {opt_mapping.get(key, key): value for key, value in options.items()}
        defaults = parser.parse_args(args=args)
        defaults = dict(defaults._get_kwargs(), **arg_options)
        # Move positional args out of options to mimic legacy optparse
        args = defaults.pop('args', ())
    else:
        # Legacy optparse method
        defaults, _ = parser.parse_args(args=[])
        defaults = dict(defaults.__dict__, **options)
    if 'skip_checks' not in options:
        defaults['skip_checks'] = True

    return command.execute(*args, **defaults)
