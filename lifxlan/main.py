import argparse
import re

from lifxlan import Device, Light
from . import LifxLAN

try:
    import typing
except ImportError:
    typing = None


def get_lights(client, args):
    # type: (LifxLAN, argparse.Namespace) -> typing.List[Light]

    if getattr(args, 'address', None):
        return [Light(mac_addr=addr, ip_addr=None) for addr in args.mac_addresses]

    client.discover_devices()
    if getattr(args, 'name', None):
        pattern = args.name
        field = lambda light: light.get_label()
    elif getattr(args, 'group', None):
        pattern = args.group
        field = lambda light: light.get_group()
    elif getattr(args, 'location', None):
        pattern = args.location
        field = lambda light: light.get_location()
    else:
        return client.lights

    return [d for d in client.lights if re.match(pattern, field(d))]


def cmd_list(client, devices, args):
    # type: (LifxLAN, typing.List[Device], argparse.Namespace) -> None

    for device in devices:
        print str(device)


def cmd_power(client, devices, args):
    # type: (LifxLAN, typing.List[Device], argparse.Namespace) -> None

    print devices
    for device in devices:
        device.set_power(args.power_level, rapid=args.rapid)


def cmd_color(client, lights, args):
    # type: (LifxLAN, typing.List[Light], argparse.Namespace) -> None

    print args


def main():
    def add_device_spec(parser):
        # type: (argparse.ArgumentParser) -> None

        device_spec = parser.add_mutually_exclusive_group(required=False)
        device_spec.add_argument_group()
        device_spec.add_argument("-n", dest='name', metavar="PATTERN",
                                 help="only devices whose name matches PATTERN")
        device_spec.add_argument("-g", dest='group', metavar="PATTERN",
                                 help="only devices belonging to groups matching PATTERN")
        device_spec.add_argument("-l", dest='location', metavar="PATTERN",
                                 help="only devices in locations matching PATTERN")
        device_spec.add_argument("-m", dest='mac_addresses', metavar="MAC_ADDR", nargs='+',
                                 help="only devices with the given MAC addresses\
                                      eg 3a:68:69:b6:98:cc")

    main_parser = argparse.ArgumentParser(description="Control Lifx devices over the LAN")

    main_parser.add_argument("-c", dest='num_devices', type=int, metavar='N', action='store',
                             help="number of devices on the LAN. this will speed up device discovery")
    main_parser.add_argument("-r", "--rapid", action='store_true', help="make set operations fire-and-forget")
    main_parser.add_argument("-v", "--verbose", action='store_true', help="be verbose")
    add_device_spec(main_parser)

    subparsers = main_parser.add_subparsers(title='commands')

    # list
    list_parser = subparsers.add_parser("list", help="list devices")
    list_parser.set_defaults(cmd=cmd_list)

    # power
    on_parser = subparsers.add_parser("on", help="turn devices on")
    on_parser.set_defaults(cmd=cmd_power, power_level='on')

    off_parser = subparsers.add_parser("off", help="turn devices off")
    off_parser.set_defaults(cmd=cmd_power, power_level='off')

    # color
    color_parser = subparsers.add_parser("color", help="set light color")
    color_parser.set_defaults(cmd=cmd_color)
    color_parser.add_argument("color", choices=['red', 'green', 'blue'])

    args = main_parser.parse_args()
    client = LifxLAN(num_lights=args.num_devices, verbose=args.verbose)
    devices = get_lights(client, args)
    args.cmd(client, devices, args)


if __name__ == '__main__':
    main()
