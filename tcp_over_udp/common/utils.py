from tcp_over_udp.common import const


def calculate_check_sum(packet):
    check_sum = 0

    for c in packet.data:
        check_sum += c

    check_sum += packet.headers.sequence_number
    check_sum += packet.headers.ack_number
    check_sum += packet.headers.data_size
    check_sum += packet.headers.flags.value

    return check_sum % (2 ** (const.CHECKSUM_SIZE * 8))


def get_ack_offset(data_size: int, flags: const.Flags) -> int:
    data_size += int(const.Flags.SYN in flags)
    data_size += int(const.Flags.FIN in flags)
    data_size += int(const.Flags.RST in flags)
    data_size += int(const.Flags.PSH in flags)
    return data_size
