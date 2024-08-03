def getMonth(month):
    """Retorna el nombre del mes

    Args:
        month (int): Numero del mes

    Returns:
        str: Nombre del mes
    """
    months = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre"
    }
    return months[month]