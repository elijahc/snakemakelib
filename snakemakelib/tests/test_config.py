# Copyright (C) 2014 by Per Unneberg
# pylint: disable=R0904
import unittest
import logging
from nose.tools import raises
from snakemakelib.config import BaseConfig, update_snakemake_config

logging.basicConfig(level=logging.DEBUG)

class TestBaseConfig(unittest.TestCase):
    """Test BaseConfig class"""
    def setUp(self):
        self.cfg = BaseConfig({'foo':'bar'})

    def tearDown(self):
        del self.cfg

    def test_create_cfg_from_dict(self):
        """Test create configuration from dictionary"""
        self.assertIsInstance(self.cfg, BaseConfig)
        self.assertDictEqual(self.cfg, {'foo':'bar'})
        self.assertListEqual(self.cfg.sections, ['foo'])

    def test_create_cfg_from_nested_dict(self):
        """Test create configuration from nested dictionary"""
        cfg = BaseConfig({'foo': BaseConfig({'bar':'foobar'})})
        self.assertIsInstance(cfg, BaseConfig)
        self.assertIsInstance(cfg['foo'], BaseConfig)
        self.assertDictEqual(cfg['foo'], {'bar':'foobar'})
        self.assertListEqual(cfg.sections, ['foo'])
        self.assertListEqual(cfg['foo'].sections, ['bar'])

    def test_create_cfg_from_args(self):
        """Test create configuration from *args"""
        cfg = BaseConfig(foo="bar", bar=BaseConfig(foo="bar", bar="foo"))
        self.assertSetEqual (set(cfg.sections), set(['bar', 'foo']))
        self.assertIsInstance(cfg['bar'], BaseConfig)
        del cfg

    def test_create_cfg_from_args_kwargs(self):
        """Test create configuration from *args and **kwargs"""
        cfg = BaseConfig(foo="bar", bar=BaseConfig(foo="bar", bar="foo"), **{'foobar':'bar', 'barfoo':BaseConfig({'foo':'bar'})})
        self.assertSetEqual (set(cfg.sections), set(['bar', 'foo', 'foobar', 'barfoo']))
        self.assertIsInstance(cfg['bar'], BaseConfig)
        self.assertIsInstance(cfg['barfoo'], BaseConfig)
        del cfg

    @raises(TypeError)
    def test_add_section_dict(self):
        """Test adding a section to config as dict"""
        self.cfg.add_section({'foobar':'bar'})

    def test_add_section_str(self):
        """Test adding a section to config as str"""
        self.cfg.add_section('foobar')
        self.assertSetEqual(set(self.cfg.sections), set(['foo', 'foobar']))

    def test_update_config(self):
        """Test updating configuration with another configuration object. """
        cfg2 = BaseConfig({'bar':'foo'})
        self.cfg.update(cfg2)
        self.assertDictEqual(self.cfg, {'foo':'bar', 'bar':'foo'})
        del cfg2

    def test_update_config_same_section(self):
        """Test updating configuration with another configuration object whose
        sections overlap. Note that this will overwrite the first
        configuration. FIXME: should this be intended behaviour?
        """
        cfg2 = BaseConfig({'foo':'foobar'})
        self.cfg.update(cfg2)
        self.assertDictEqual(self.cfg, {'foo':'foobar'})
        del cfg2

    def test_update_config_nested(self):
        """Test updating configuration with another nested configuration"""
        cfg2 = BaseConfig({'bar': BaseConfig({'foo':'bar'})})
        self.cfg.update(cfg2)
        self.assertDictEqual(self.cfg, {'foo':'bar', 'bar':{'foo':'bar'}})
        del cfg2

    def test_setting_config_section_to_dict(self):
        """Test setting a configuration section to a dict"""
        self.cfg['foo'] = {'foo':'bar'}
        self.assertIsInstance(self.cfg['foo'], BaseConfig)

    def test_baseconfig_from_nested_dictionary(self):
        """Instantiate BaseConfig object from nested dictionary"""
        d = BaseConfig({'foo':'bar', 'bar' : {'foo':'bar', 'bar':{'foo':'bar', 'bar':{'foo':'bar'}}}})
        def assert_sections(d):
            for k,v in d.items():
                if isinstance(v,dict):
                    self.assertIsInstance(v, BaseConfig)
        assert_sections(d)

    def test_getitem(self):
        """Test getting an item from BaseConfig"""
        d = BaseConfig({'foo' : {'bar' : 'foo'}, 'bar' : lambda: "bar", 'foobar' : lambda x: x, 'barfoo' : lambda x: x['foo'], 'foofoo' : None})
        self.assertIsInstance(d['foo'], BaseConfig)
        self.assertDictEqual(d['foo'], {'bar' : 'foo'})
        self.assertIsInstance(d['foo']['bar'], str)
        self.assertEqual(d['foo']['bar'], 'foo')
        self.assertIsInstance(d['bar'], str)
        self.assertEqual(d['bar'], 'bar')
        self.assertIsInstance(d['foobar', "test"], str)
        self.assertEqual(d['foobar', "test"], "test")
        self.assertIsInstance(d['barfoo', {'foo' : "test"}], str)
        self.assertEqual(d['barfoo', {'foo' : "test"}], "test")
        self.assertIsNone (d['foofoo'])

class TestSmlConfig(unittest.TestCase):
    def setUp(self):
        self.cfg = BaseConfig({
            'bar' : BaseConfig({
                'foo' : 'customfoo',
            })
        })
        self.cfg_nested = BaseConfig({
            'bar' : BaseConfig({
                'bar' : BaseConfig({
                    'bar':'customfoo'
                })
            })
        })

        self.default = BaseConfig({
            'foo':'bar',
            'bar' : BaseConfig({
                'foo' : 'foobar',
                'bar' : 'foo'
            })
        })
        self.default_nested = BaseConfig({
            'foo':'bar',
            'bar' : BaseConfig({
                'foo' : 'foobar',
                'bar' : BaseConfig({
                    'foo' : 'bar'
                })
            })
        })
        self.cfg_list = BaseConfig({
            'foo' : 'bar',
            'bar' : ['foo', 'bar'],
        })
        
    def tearDown(self):
        del self.cfg
        del self.cfg_list
        del self.cfg_nested
        del self.default
        del self.default_nested

    def test_init_sml_config_from_dict(self):
        cfg = BaseConfig({'foo':'bar'})
        self.assertIsInstance(cfg, BaseConfig)
        self.assertDictEqual(cfg, {'foo': 'bar'})

    def test_init_sml_config(self):
        """Test initalizing the sml config object"""
        cfg = BaseConfig(BaseConfig({'foo':'bar'}))
        self.assertDictEqual(cfg, {'foo': 'bar'})

    def test_update_sml_config_from_init(self):
        """Test initializing the sml config object from an init"""
        cfg = BaseConfig(self.cfg)
        cfg = update_snakemake_config(cfg, self.cfg_nested)
        self.assertDictEqual(cfg, {'bar': {'bar': {'bar': 'customfoo'}, 'foo': 'customfoo'}})

    def test_update_sml_config_with_default(self):
        """Test updating a configuration object skipping values that are
        already in use. Overriding dict.update will not do as its original
        intedend behaviour is needed.

        What is the desired behaviour?

        1. In Snakefile user modifies a custom configuration object
        2. Relevant include files are loaded with default settings.

        3. Default settings need to be updated with custom config at
           once so that custom changes are reflected in rules (is this
           true?)
        """
        cfg = update_snakemake_config(self.cfg, self.default)
        self.assertDictEqual(cfg, {'bar': {'bar': 'foo', 'foo': 'customfoo'}, 'foo': 'bar'})

    def test_update_sml_config_with_default_nested(self):
        cfg = update_snakemake_config(self.cfg, self.default_nested)
        self.assertDictEqual(cfg, {'foo': 'bar', 'bar': {'foo': 'customfoo', 'bar': {'foo': 'bar'}}})

    def test_update_sml_config_with_both_nested(self):
        """Test updating a configuration object where both are nested. Note that in this example  self.cfg_nested has a key (section) not defined in default so a warning should be raised. In other words, at a given level, if default is a BaseConfig, the keys in config should be a subset of keys in default."""
        cfg = update_snakemake_config(self.cfg_nested, self.default_nested)
        self.assertDictEqual(cfg, {'foo': 'bar', 'bar': {'foo': 'foobar', 'bar': {'foo': 'bar', 'bar': 'customfoo'}}})

    @raises(TypeError)
    def test_update_sml_config_with_cfg_nested_missing_base_config(self):
        """Test updating sml config where value for section is string in custom config and BaseConfig in default"""
        cfg = BaseConfig({
            'bar' : BaseConfig({
                'bar' : 'test'
                })
            })
        cfg = update_snakemake_config(cfg, self.default_nested)

    @raises(TypeError)
    def test_update_sml_config_with_string(self):
        cfg = "foo"
        update_snakemake_config(cfg, {})

    def test_get_sml_config_section(self):
        """Test getting a config section section"""
        cfg = BaseConfig(self.cfg_nested)
        cfg = update_snakemake_config(cfg, self.default_nested)
        self.assertDictEqual(cfg['bar'], {'bar': {'bar': 'customfoo', 'foo': 'bar'}, 'foo': 'foobar'})

    def test_set_sml_config_with_list(self):
        """Test setting an sml_config object with a list value"""
        cfg = BaseConfig(self.cfg_list)
        self.assertIsInstance(cfg['bar'], list)
        self.assertListEqual(cfg['bar'], ['foo', 'bar'])

    def test_update_sml_config_with_function(self):
        """Test setting an sml_config object with a function that requires a parameter"""
        cfg = BaseConfig(self.cfg)
        cfg = update_snakemake_config(cfg, {'foo':lambda x: x})
        self.assertEqual(str(type(dict(cfg)['foo'])), "<class 'function'>")
