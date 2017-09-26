# Copyright 2017 Neverware Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


VENV ?= venv


all: lint test


clean:
	rm -rf build/ dist/


dist:
	python setup.py bdist_wheel --universal


lint:
	${VENV}/bin/pylint ebuild_util setup.py test


test:
	${VENV}/bin/python -m unittest discover


.PHONY: all clean dist lint test