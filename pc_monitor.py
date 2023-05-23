#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""Монитор системных ресурсов компьютера
Создатель: OkulusDev (C) 2023
Лицензия: GNU GPL v3"""
import os
import sys
import platform
from datetime import datetime
import logging
import psutil


def get_size(bytes: int, suffix: str='B') -> str:
	"""Получаем размер из байтов в более большие форматы. Доступны:
	килобайты, мегабайты, гигабайты, терабайты, петабайты.
	Аргументы:
	 + bytes: int - количество байтов
	 + suffix: str - тип суффикса
	Возвращает:
	 + str - размер"""
	factor = 1024

	for unit in ["", "K", "M", "G", "T", "P"]:
		if bytes < factor:
			return f'{bytes:.2f}{unit}{suffix}'
		bytes /= factor


def print_log(text: str) -> None:
	"""Вывод на экран и в лог-файл
	Аргументы:
	 + text: str - текст для вывода"""
	logging.info(text)
	print(text)


def start_logger() -> None:
	"""Создаем базовый конфиг логгера
	Логи сохраняются в каталог в файл computer_resources.log
	Формат: время [уровень лога] сообщение"""
	logging.basicConfig(level=logging.INFO, filename="data/computer_resources.log", 
						filemode="w", format="%(asctime)s [%(levelname)s] %(message)s")


class ResourceMonitor:
	"""Монитор системных ресурсов компьютера"""
	def __init__(self):
		# Инициализация объекта - создание переменных
		self.uname = platform.uname()
		self.cpufreq = psutil.cpu_freq()
		self.swap = psutil.swap_memory()
		self.svmem = psutil.virtual_memory()
		self.partitions = psutil.disk_partitions()
		self.if_addrs = psutil.net_if_addrs()
		self.net_io = psutil.net_io_counters()

	def call_all(self):
		# Вызов всех функций
		self.system_info()
		self.proc_info()
		self.ram_info()
		self.disk_info()
		self.network_info()

	def system_info(self):
		# Общая информация о системе
		print('=' * 10, 'Информация о системе', '=' * 10)
		logging.info('Информация о системе')
		print_log(f'Система: {self.uname.system}')
		print_log(f'Имя сетевого узла: {self.uname.node}')
		print_log(f'Выпуск: {self.uname.release}')
		print_log(f'Версия: {self.uname.version}')
		print_log(f'Машина: {self.uname.machine}')
		print_log(f'Процессор: {self.uname.processor}')

	def proc_info(self):
		# Информация о процессоре
		print('=' * 10, 'Информация о процессоре', '=' * 10)
		logging.info('Информация о процессоре')
		print_log(f'Физические ядра: {psutil.cpu_count(logical=False)}')
		print_log(f'Количество ядер: {psutil.cpu_count(logical=True)}')
		print_log(f'Маскимальная частота процессора: {self.cpufreq.max:.2f}МГц')
		print_log(f'Минимальная частота процессора: {self.cpufreq.min:.2f}МГц')
		print_log(f'Текущая частота процессора: {self.cpufreq.current:.2f}МГц')
		for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
			print_log(f'Загруженность ядра {i}: {percentage}%')
		print_log(f'Общая загруженность процессора: {psutil.cpu_percent()}%')

	def network_info(self):
		# Информация о сети
		print('=' * 10, 'Информация о сети', '=' * 10)
		logging.info('Информация о сети')
		for inteface_name, interface_addresses in self.if_addrs.items():
			for address in interface_addresses:
				print('=' * 5, f'Информация о интерфейсе сети: {inteface_name}', '=' * 5)
				logging.info(f'Информация о интерфейсе сети: {inteface_name}')
				if str(address.family) == 'AddressFamily.AF_INET':
					print_log(f'Тип интерфейса сети {inteface_name}: {str(address.family)}')
					print_log(f'IP интерфейса сети {inteface_name}: {address.address}')
					print_log(f'Сетевая маска интерфейса сети {inteface_name}: {address.netmask}')
					print_log(f'Широковещательный IP-адрес интерфейса сети {inteface_name}: {address.broadcast}')
				elif str(address.family) == 'AddressFamily.AF_PACKET':
					print_log(f'Тип интерфейса сети {inteface_name}: {str(address.family)}')
					print_log(f'MAC-адрес интерфейса сети {inteface_name}: {address.address}')
					print_log(f'Сетевая маска интерфейса сети {inteface_name}: {address.netmask}')
					print_log(f'Широковещательный IP-адрес интерфейса сети {inteface_name}: {address.broadcast}')
				else:
					print_log(f'Тип интерфейса сети {inteface_name}: {str(address.family)}')
					print_log(f'MAC-адрес интерфейса сети {inteface_name}: {address.address}')
					print_log(f'Сетевая маска интерфейса сети {inteface_name}: {address.netmask}')
					print_log(f'Широковещательный IP-адрес интерфейса сети {inteface_name}: {address.broadcast}')
		print_log(f'Общее количество отправленных байтов: {get_size(self.net_io.bytes_sent)}')
		print_log(f'Общее количество полученных байтов: {get_size(self.net_io.bytes_recv)}')

	def disk_info(self):
		# Информация о разделах диска
		print('=' * 10, 'Информация о дисках', '=' * 10)
		logging.info('Информация о дисках')
		for partition in self.partitions:
			print('=' * 5, f'Информация о разделе диска: {partition.device}', '=' * 5)
			logging.info(f'Информация о разделе диска: {partition.device}')
			print_log(f'Файловая система раздела диска {partition.device}: {partition.fstype}')
			try:
				partition_usage = psutil.disk_usage(partition.mountpoint)
			except PermissionError:
				continue
			print_log(f'Общий обьем раздела диска {partition.device}: {get_size(partition_usage.total)}')
			print_log(f'Используемый обьем раздела диска {partition.device}: {get_size(partition_usage.used)}')
			print_log(f'Свободный обьем раздела диска {partition.device}: {get_size(partition_usage.free)}')
			print_log(f'Процент объема раздела диска {partition.device}: {get_size(partition_usage.percent)}')

	def ram_info(self):
		# Информация об оперативной памяти и памяти подкачки
		print('=' * 10, 'Информация об ОЗУ', '=' * 10)
		logging.info('Информация об ОЗУ')
		print_log(f'Объем ОЗУ: {get_size(self.svmem.total)}')
		print_log(f'Доступно ОЗУ: {get_size(self.svmem.available)}')
		print_log(f'Используется ОЗУ: {get_size(self.svmem.used)}')
		print_log(f'Процент ОЗУ: {get_size(self.svmem.percent)}')
		if self.swap:
			print('=' * 5, 'Информация о памяти подкачки', '=' * 5)
			logging.info('Информация о памяти подкачки')
			print_log(f'Объем памяти подкачки: {get_size(self.swap.total)}')
			print_log(f'Свободно памяти подкачки: {get_size(self.swap.free)}')
			print_log(f'Используется памяти подкачки: {get_size(self.swap.used)}')
			print_log(f'Процент памяти подкачки: {self.swap.percent}%')


def start_pc_monitor():
	# Старт логгера
	start_logger()

	# Запускаем монитор ресурсов
	monitor = ResourceMonitor()
	monitor.call_all()


if __name__ == '__main__':
	start_pc_monitor()
