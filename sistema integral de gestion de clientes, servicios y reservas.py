
import abc
import datetime
import logging
from typing import List, Optional, Union

# Setup logging
logging.basicConfig(
    filename='software_fj.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Custom Exceptions
class SoftwareFJException(Exception):
    """Base exception for Software FJ system."""
    pass

class InvalidDataError(SoftwareFJException):
    """Raised when data is invalid."""
    pass

class MissingParameterError(SoftwareFJException):
    """Raised when a required parameter is missing."""
    pass

class OperationNotAllowedError(SoftwareFJException):
    """Raised when an operation is not allowed."""
    pass

class ReservationError(SoftwareFJException):
    """Raised for errors related to reservations."""
    pass

class ServiceUnavailableError(SoftwareFJException):
    """Raised when a service is not available."""
    pass

class CalculationError(SoftwareFJException):
    """Raised when cost calculation is inconsistent."""
    pass

# Abstract base class for entities
class Entity(abc.ABC):
    @abc.abstractmethod
    def get_id(self) -> str:
        pass

# Cliente class with encapsulation and validations
class Cliente(Entity):
    def __init__(self, dni: str, nombre: str, apellido: str, email: str, telefono: str):
        try:
            self._dni = None
            self._nombre = None
            self._apellido = None
            self._email = None
            self._telefono = None

            self.dni = dni
            self.nombre = nombre
            self.apellido = apellido
            self.email = email
            self.telefono = telefono
        except Exception as e:
            logging.error(f"Error creating Cliente: {e}", exc_info=True)
            raise

    @property
    def dni(self) -> str:
        return self._dni

    @dni.setter
    def dni(self, value: str):
        if not value or not value.isdigit() or len(value) < 6:
            raise InvalidDataError("DNI inválido: debe ser numérico y al menos 6 dígitos.")
        self._dni = value

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, value: str):
        if not value or not value.isalpha():
            raise InvalidDataError("Nombre inválido: debe contener solo letras.")
        self._nombre = value.capitalize()

    @property
    def apellido(self) -> str:
        return self._apellido

    @apellido.setter
    def apellido(self, value: str):
        if not value or not value.isalpha():
            raise InvalidDataError("Apellido inválido: debe contener solo letras.")
        self._apellido = value.capitalize()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        if not value or "@" not in value or "." not in value:
            raise InvalidDataError("Email inválido.")
        self._email = value.lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, value: str):
        if not value or not value.isdigit() or len(value) < 7:
            raise InvalidDataError("Teléfono inválido: debe ser numérico y al menos 7 dígitos.")
        self._telefono = value

    def get_id(self) -> str:
        return self.dni

    def __str__(self):
        return f"Cliente {self.nombre} {self.apellido} (DNI: {self.dni})"

# Abstract Servicio class
class Servicio(abc.ABC):
    def __init__(self, codigo: str, descripcion: str, base_cost: float):
        if not codigo:
            raise MissingParameterError("Código de servicio es obligatorio.")
        if base_cost < 0:
            raise InvalidDataError("Costo base no puede ser negativo.")
        self.codigo = codigo
        self.descripcion = descripcion
        self.base_cost = base_cost

    @abc.abstractmethod
    def calcular_costo(self, *args, **kwargs) -> float:
        pass

    @abc.abstractmethod
    def validar_parametros(self, *args, **kwargs):
        pass

    def describir(self) -> str:
        return f"Servicio {self.codigo}: {self.descripcion} - Costo base: {self.base_cost:.2f}"

# Servicio Sala (reservas de salas)
class ServicioSala(Servicio):
    def __init__(self, codigo: str, descripcion: str, base_cost: float, capacidad: int):
        super().__init__(codigo, descripcion, base_cost)
        if capacidad <= 0:
            raise InvalidDataError("Capacidad debe ser mayor que cero.")
        self.capacidad = capacidad

    def validar_parametros(self, duracion_horas: int, asistentes: int):
        if duracion_horas <= 0:
            raise InvalidDataError("Duración debe ser mayor que cero.")
        if asistentes <= 0 or asistentes > self.capacidad:
            raise InvalidDataError(f"Asistentes deben ser entre 1 y {self.capacidad}.")

    # Método sobrecargado: calcular_costo con o sin impuestos y descuentos
    def calcular_costo(self, duracion_horas: int, asistentes: int,
                       impuesto: Optional[float] = None,
                       descuento: Optional[float] = None) -> float:
        try:
            self.validar_parametros(duracion_horas, asistentes)
            cost = self.base_cost * duracion_horas
            if impuesto is not None:
                if not (0 <= impuesto <= 1):
                    raise InvalidDataError("Impuesto debe estar entre 0 y 1.")
                cost += cost * impuesto
            if descuento is not None:
                if not (0 <= descuento <= 1):
                    raise InvalidDataError("Descuento debe estar entre 0 y 1.")
                cost -= cost * descuento
            if cost < 0:
                raise CalculationError("Costo calculado no puede ser negativo.")
            return round(cost, 2)
        except Exception as e:
            logging.error(f"Error calcular_costo ServicioSala: {e}", exc_info=True)
            raise

    def describir(self) -> str:
        return f"Sala {self.codigo}: {self.descripcion}, Capacidad: {self.capacidad}, Costo base por hora: {self.base_cost:.2f}"

# Servicio Equipo (alquiler de equipos)
class ServicioEquipo(Servicio):
    def __init__(self, codigo: str, descripcion: str, base_cost: float, tipo_equipo: str):
        super().__init__(codigo, descripcion, base_cost)
        if not tipo_equipo:
            raise MissingParameterError("Tipo de equipo es obligatorio.")
        self.tipo_equipo = tipo_equipo

    def validar_parametros(self, duracion_dias: int):
        if duracion_dias <= 0:
            raise InvalidDataError("Duración debe ser mayor que cero.")

    def calcular_costo(self, duracion_dias: int,
                       impuesto: Optional[float] = None,
                       descuento: Optional[float] = None,
                       seguro: Optional[float] = None) -> float:
        try:
            self.validar_parametros(duracion_dias)
            cost = self.base_cost * duracion_dias
            if seguro is not None:
                if seguro < 0:
                    raise InvalidDataError("Seguro no puede ser negativo.")
                cost += seguro
            if impuesto is not None:
                if not (0 <= impuesto <= 1):
                    raise InvalidDataError("Impuesto debe estar entre 0 y 1.")
                cost += cost * impuesto
            if descuento is not None:
                if not (0 <= descuento <= 1):
                    raise InvalidDataError("Descuento debe estar entre 0 y 1.")
                cost -= cost * descuento
            if cost < 0:
                raise CalculationError("Costo calculado no puede ser negativo.")
            return round(cost, 2)
        except Exception as e:
            logging.error(f"Error calcular_costo ServicioEquipo: {e}", exc_info=True)
            raise

    def describir(self) -> str:
        return f"Equipo {self.codigo}: {self.descripcion}, Tipo: {self.tipo_equipo}, Costo base por día: {self.base_cost:.2f}"

# Servicio Asesoria (asesorías especializadas)
class ServicioAsesoria(Servicio):
    def __init__(self, codigo: str, descripcion: str, base_cost: float, especialista: str):
        super().__init__(codigo, descripcion, base_cost)
        if not especialista:
            raise MissingParameterError("Especialista es obligatorio.")
        self.especialista = especialista

    def validar_parametros(self, duracion_horas: int):
        if duracion_horas <= 0:
            raise InvalidDataError("Duración debe ser mayor que cero.")

    def calcular_costo(self, duracion_horas: int,
                       impuesto: Optional[float] = None,
                       descuento: Optional[float] = None,
                       tarifa_extra: Optional[float] = None) -> float:
        try:
            self.validar_parametros(duracion_horas)
            cost = self.base_cost * duracion_horas
            if tarifa_extra is not None:
                if tarifa_extra < 0:
                    raise InvalidDataError("Tarifa extra no puede ser negativa.")
                cost += tarifa_extra
            if impuesto is not None:
                if not (0 <= impuesto <= 1):
                    raise InvalidDataError("Impuesto debe estar entre 0 y 1.")
                cost += cost * impuesto
            if descuento is not None:
                if not (0 <= descuento <= 1):
                    raise InvalidDataError("Descuento debe estar entre 0 y 1.")
                cost -= cost * descuento
            if cost < 0:
                raise CalculationError("Costo calculado no puede ser negativo.")
            return round(cost, 2)
        except Exception as e:
            logging.error(f"Error calcular_costo ServicioAsesoria: {e}", exc_info=True)
            raise

    def describir(self) -> str:
        return f"Asesoría {self.codigo}: {self.descripcion}, Especialista: {self.especialista}, Costo base por hora: {self.base_cost:.2f}"

# Reserva class integrating cliente, servicio, duración y estado
class Reserva:
    ESTADOS_VALIDOS = {'pendiente', 'confirmada', 'cancelada', 'procesada'}

    def __init__(self, cliente: Cliente, servicio: Servicio, duracion: Union[int, float]):
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = 'pendiente'
        self.fecha_reserva = datetime.datetime.now()
        self.costo_final = None

    def confirmar(self):
        try:
            if self.estado != 'pendiente':
                raise OperationNotAllowedError("Solo reservas pendientes pueden ser confirmadas.")
            self.estado = 'confirmada'
            logging.info(f"Reserva confirmada: {self}")
        except Exception as e:
            logging.error(f"Error al confirmar reserva: {e}", exc_info=True)
            raise

    def cancelar(self):
        try:
            if self.estado not in {'pendiente', 'confirmada'}:
                raise OperationNotAllowedError("Solo reservas pendientes o confirmadas pueden ser canceladas.")
            self.estado = 'cancelada'
            logging.info(f"Reserva cancelada: {self}")
        except Exception as e:
            logging.error(f"Error al cancelar reserva: {e}", exc_info=True)
            raise

    def procesar(self, **kwargs):
        try:
            if self.estado != 'confirmada':
                raise OperationNotAllowedError("Solo reservas confirmadas pueden ser procesadas.")
            # Calcular costo con parámetros opcionales
            self.costo_final = self.servicio.calcular_costo(self.duracion, **kwargs)
            self.estado = 'procesada'
            logging.info(f"Reserva procesada: {self} - Costo final: {self.costo_final}")
        except Exception as e:
            logging.error(f"Error al procesar reserva: {e}", exc_info=True)
            raise

    def __str__(self):
        return (f"Reserva de {self.cliente} para servicio [{self.servicio.codigo}] "
                f"duración: {self.duracion}, estado: {self.estado}")

# Sistema Integral de Gestión
class SistemaGestion:
    def __init__(self):
        self.clientes: List[Cliente] = []
        self.servicios: List[Servicio] = []
        self.reservas: List[Reserva] = []

    # Cliente management
    def agregar_cliente(self, cliente: Cliente):
        try:
            if any(c.dni == cliente.dni for c in self.clientes):
                raise OperationNotAllowedError(f"Cliente con DNI {cliente.dni} ya existe.")
            self.clientes.append(cliente)
            logging.info(f"Cliente agregado: {cliente}")
        except Exception as e:
            logging.error(f"Error al agregar cliente: {e}", exc_info=True)
            raise

    # Servicio management
    def agregar_servicio(self, servicio: Servicio):
        try:
            if any(s.codigo == servicio.codigo for s in self.servicios):
                raise OperationNotAllowedError(f"Servicio con código {servicio.codigo} ya existe.")
            self.servicios.append(servicio)
            logging.info(f"Servicio agregado: {servicio.describir()}")
        except Exception as e:
            logging.error(f"Error al agregar servicio: {e}", exc_info=True)
            raise

    # Reserva management
    def crear_reserva(self, dni_cliente: str, codigo_servicio: str, duracion: Union[int, float]) -> Reserva:
        try:
            cliente = next((c for c in self.clientes if c.dni == dni_cliente), None)
            if cliente is None:
                raise ReservationError(f"Cliente con DNI {dni_cliente} no encontrado.")
            servicio = next((s for s in self.servicios if s.codigo == codigo_servicio), None)
            if servicio is None:
                raise ServiceUnavailableError(f"Servicio con código {codigo_servicio} no disponible.")
            reserva = Reserva(cliente, servicio, duracion)
            self.reservas.append(reserva)
            logging.info(f"Reserva creada: {reserva}")
            return reserva
        except Exception as e:
            logging.error(f"Error al crear reserva: {e}", exc_info=True)
            raise

    def listar_clientes(self):
        return list(self.clientes)

    def listar_servicios(self):
        return list(self.servicios)

    def listar_reservas(self):
        return list(self.reservas)

# Simulación de operaciones
def simulacion_operaciones():
    sistema = SistemaGestion()

    # 1. Registro válido de cliente
    try:
        c1 = Cliente("12345678", "Ana", "Perez", "ana.perez@example.com", "1234567")
        sistema.agregar_cliente(c1)
    except Exception as e:
        print(f"Error registro cliente 1: {e}")

    # 2. Registro inválido de cliente (email inválido)
    try:
        c2 = Cliente("87654321", "Luis", "Gomez", "luis.gomez#example.com", "7654321")
        sistema.agregar_cliente(c2)
    except Exception as e:
        print(f"Error registro cliente 2: {e}")

    # 3. Registro válido de servicio sala
    try:
        s1 = ServicioSala("SALA01", "Sala de reuniones principal", 100.0, 20)
        sistema.agregar_servicio(s1)
    except Exception as e:
        print(f"Error registro servicio sala: {e}")

    # 4. Registro inválido de servicio sala (capacidad negativa)
    try:
        s2 = ServicioSala("SALA02", "Sala pequeña", 50.0, -5)
        sistema.agregar_servicio(s2)
    except Exception as e:
        print(f"Error registro servicio sala inválido: {e}")

    # 5. Registro válido de servicio equipo
    try:
        s3 = ServicioEquipo("EQUIP01", "Proyector HD", 30.0, "Proyector")
        sistema.agregar_servicio(s3)
    except Exception as e:
        print(f"Error registro servicio equipo: {e}")

    # 6. Registro válido de servicio asesoría
    try:
        s4 = ServicioAsesoria("ASES01", "Asesoría en desarrollo", 150.0, "Ing. Ramirez")
        sistema.agregar_servicio(s4)
    except Exception as e:
        print(f"Error registro servicio asesoría: {e}")

    # 7. Crear reserva válida
    try:
        reserva1 = sistema.crear_reserva("12345678", "SALA01", 3)
        reserva1.confirmar()
        reserva1.procesar(impuesto=0.18, descuento=0.1)
        print(f"Reserva procesada con costo: {reserva1.costo_final}")
    except Exception as e:
        print(f"Error reserva 1: {e}")

    # 8. Crear reserva inválida (cliente no existe)
    try:
        reserva2 = sistema.crear_reserva("00000000", "SALA01", 2)
    except Exception as e:
        print(f"Error reserva 2: {e}")

    # 9. Crear reserva inválida (servicio no existe)
    try:
        reserva3 = sistema.crear_reserva("12345678", "NOEXISTE", 2)
    except Exception as e:
        print(f"Error reserva 3: {e}")

    # 10. Crear reserva con parámetros inválidos (duración negativa)
    try:
        reserva4 = sistema.crear_reserva("12345678", "EQUIP01", -1)
        reserva4.confirmar()
        reserva4.procesar()
    except Exception as e:
        print(f"Error reserva 4: {e}")

    # 11. Cancelar reserva válida
    try:
        reserva5 = sistema.crear_reserva("12345678", "ASES01", 2)
        reserva5.confirmar()
        reserva5.cancelar()
        print(f"Reserva cancelada: {reserva5}")
    except Exception as e:
        print(f"Error reserva 5: {e}")

    # 12. Intentar procesar reserva cancelada (no permitido)
    try:
        reserva5.procesar()
    except Exception as e:
        print(f"Error procesar reserva cancelada: {e}")

    # 13. Crear y procesar reserva asesoría con tarifa extra
    try:
        reserva6 = sistema.crear_reserva("12345678", "ASES01", 4)
        reserva6.confirmar()
        reserva6.procesar(impuesto=0.18, tarifa_extra=50)
        print(f"Reserva asesoría procesada con costo: {reserva6.costo_final}")
    except Exception as e:
        print(f"Error reserva 6: {e}")

    # 14. Crear y procesar reserva equipo con seguro y descuento
    try:
        reserva7 = sistema.crear_reserva("12345678", "EQUIP01", 5)
        reserva7.confirmar()
        reserva7.procesar(impuesto=0.18, descuento=0.05, seguro=20)
        print(f"Reserva equipo procesada con costo: {reserva7.costo_final}")
    except Exception as e:
        print(f"Error reserva 7: {e}")

    # 15. Intentar agregar cliente duplicado
    try:
        c3 = Cliente("12345678", "Ana", "Perez", "ana.perez@example.com", "1234567")
        sistema.agregar_cliente(c3)
    except Exception as e:
        print(f"Error cliente duplicado: {e}")

    # Mostrar resumen final
    print("\nClientes registrados:")
    for c in sistema.listar_clientes():
        print(f" - {c}")

    print("\nServicios registrados:")
    for s in sistema.listar_servicios():
        print(f" - {s.describir()}")

    print("\nReservas registradas:")
    for r in sistema.listar_reservas():
        print(f" - {r}")

if __name__ == "__main__":
    try:
        simulacion_operaciones()
    except Exception as e:
        logging.critical(f"Error crítico en la simulación: {e}", exc_info=True)
        print(f"Error crítico en la simulación: {e}")
