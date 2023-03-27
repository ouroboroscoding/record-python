# coding=utf8
"""Record Storage

Extends the Tree class to add storage capabilities for Records
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__email__		= "chris@ouroboroscoding.com"
__created__		= "2023-03-21"

# Limit imports
__all__ = ['Storage']

# Python imports
import abc

# Pip imports
from define import Tree, NOT_SET
from tools import combine

# Local imports
from .data import Data
from .types import Limit

class Storage(Tree, abc.ABC):
	"""Storage

	Represents the top level definition of some sort of stored record

	Extends define.Tree in order to add the ability to validate and clean up
	data in the record

	Extends:
		define.Tree
	"""

	@abc.abstractmethod
	def add(self, value: dict | list) -> str | list:
		"""Add

		Adds one or more raw records to the storage system

		Arguments:
			value (dict | dict[]): One or more dictionaries of fields to data

		Returns:
			The ID or IDs of the added records
		"""
		pass

	@abc.abstractmethod
	def create(self, value: dict | list = {}) -> Data | list:
		"""Create

		Creates one or more new data objects associated with the Storage
		instance

		Arguments:
			value (dict | list): The initial values to set for the record(s)

		Returns:
			Data | Data[]
		"""
		pass

	@abc.abstractmethod
	def count(self, filter: dict = None) -> int:
		"""Count

		Returns the count of records, with or without a filter

		Arguments:
			filter (dict): Optional, data to filter the count of records by

		Returns:
			int
		"""
		pass

	@abc.abstractmethod
	def exists(self, _id: str):
		"""Exists

		Returns True if the specified ID is found in the storage system

		Arguments:
			_id (str): The ID to check for

		Returns:
			bool
		"""
		pass

	@abc.abstractmethod
	def fetch(self,
		_id: str | list = None,
		filter: dict = None,
		limit: int | Limit = None,
		fields: list = None,
		raw: bool | list = False,
		options: dict = None
	) -> list | dict | Data:
		"""Fetch

		Gets one, many, or all records from the storage system associated with
		the class instance through one or more checks against IDs, filters, and
		limits. Passing no arguments at all will return every record available

		Arguments:
			_id: (str | str[]): The ID or IDs used to get the records
			filter (dict): Data to filter the count of records by
			limit (int | Limit): The limit to set for the fetch
			fields (str[]): A list of the fields to be returned for each record
			raw (bool): If true, dicts are returned instead of Data instances
			options (dict): Custom options processed by the storage system

		Returns:
			Data | Data[] | dict | dict[]
		"""
		pass

	@abc.abstractmethod
	def install(self) -> bool:
		"""Install

		Installs or creates the location where the records will be stored and
		retrieved from

		Returns:
			bool
		"""
		pass

	@abc.abstractmethod
	def remove(self, _id: str | list = None, filter: dict = None):
		"""Remove

		Removes one or more records from storage by ID or filter

		Arguments:
			"""
		pass

	@abc.abstractmethod
	def revision_add(cls, _id: str, changes: dict):
		"""Revision Add

		Adds data to the storage system associated with the record that
		indicates the changes since the previous add/save

		Arguments:
			_id (str): The ID of the record the change is associated with
			changes (dict): The dictionary of changes to add

		Returns:
			bool
		"""
		pass

	@classmethod
	def revision_generate(cls, old: dict | list, new: dict | list) -> dict | None:
		"""Revision Generate

		Generates the list of changes between two records

		Arguments:
			old (dict | list): Old record
			new (dict | list): New record

		Returns:
			dict | None
		"""

		# If we are dealing with a dict
		if isinstance(old, dict):

			# If the new is not also a dict
			if not isinstance(new, dict):
				return { 'old': old, 'new': new }

			# Both are dicts, create a new dict to return
			dRet = {}

			# Get the length of keys in old
			iOldLen = len(old.keys())

			# Store the keys from new and get the length
			lNewKeys = list(new.keys())
			iNewLen = len(lNewKeys)

			# Start checking keys from old
			for k in old:

				# If the key doesn't exist in new
				if k not in new:
					dRet[k] = { 'old': old[k], 'new': None }
					continue

				# It exists in both so pass the two along and remove the key
				#	from the new list
				dTemp = cls.generate_changes(old[k], new[k])
				lNewKeys.remove(k)

				# If there's a value, store it
				if dTemp:
					dRet[k] = dTemp

			# If there's any keys left in the new list
			if lNewKeys:
				for k in lNewKeys:
					dRet[k] = { 'old': None, 'new': new[k] }

			# If the number of keys that are different match the total number of
			#	keys, set everything as changed
			iMaxKeys = iOldLen > iNewLen and iOldLen or iNewLen
			if len(dRet.keys()) >= iMaxKeys:
				return { 'old': old, 'new': new }

			# Return the changes if there are any
			if dRet:
				return dRet

		# Else if we are dealing with a list
		elif isinstance(old, list):

			# If the new is not also a list
			if not isinstance(new, list):
				return { 'old': old, 'new': new }

			# Both are lists, create a new dict to return
			dRet = {}

			# Get the length of the old and new
			iOldLen = len(old)
			iNewLen = len(new)

			# Start going through the indexes of the old
			for i in range(iOldLen):

				# If it's not in the new
				if i >= iNewLen:
					dRet[str(i)] = { 'old': old[i], 'new': None }
					continue

				# It exists in both so pass the two along
				dTemp = cls.generate_changes(old[i], new[i])

				# If there's a value, store it
				if dTemp: dRet[str(i)] = dTemp

			# If there's more new indexes than old
			if iNewLen > iOldLen:
				for i in range(iOldLen, iNewLen):
					dRet[str(i)] = { 'old': None, 'new': new[i] }

			# If the number of indexes different match all data, set everything
			#	as changed
			iMaxKeys = iOldLen > iNewLen and iOldLen or iNewLen
			if len(dRet.keys()) >= iMaxKeys:
				return { 'old': old, 'new': new }

			# Return the changes if there are any
			if dRet: return dRet

		# Else it's a single value
		else:

			# If the new is a dict or list or the values don't match
			if isinstance(new, (dict,list)) or new != old:
				return { 'old': old, 'new': new }

		# No changes
		return None

	@abc.abstractmethod
	def uninstall(self) -> bool:
		"""Uninstall

		Uninstalls or deletes the location where the records will be stored and
		retrieved from

		Returns:
			bool
		"""
		pass