from functools import update_wrapper
import types
import unittest

from mock import mock
from mock import patch

from lib.factories import config_factory
from lib.factories import suite_factory
from seismograph import collector
from seismograph import exceptions
from seismograph import loader
from seismograph import suite


def compose_decorators(*decs):
    def decorator(f):
        for dec in reversed(decs):
            f = dec(update_wrapper(f, decorator))
        return f

    return decorator


def mock_try_apply_rules(_, rules):
    for x in rules:
        rules.remove(x)


class GetShuffleTestCase(unittest.TestCase):
    def test_get_shuffle_no_params(self):
        fake_config = config_factory.create()
        return_value = collector.get_shuffle(fake_config)
        self.assertIsNone(return_value)

    def test_get_shuffle_return_values(self):
        fake_config = config_factory.create(**{
            'RANDOM': True,
            'RANDOM_SEED': 1,
        })
        return_value = collector.get_shuffle(fake_config)
        self.assertIsInstance(return_value, types.MethodType)

    def test_get_shuffle_raises(self):
        with self.assertRaises(AttributeError):
            collector.get_shuffle(None)


class GetSuiteNameFromCommandTestCase(unittest.TestCase):
    def test_get_suite_name_from_command(self):
        test_command = '1:1'
        return_value = collector.get_suite_name_from_command(test_command)
        self.assertEqual('1', return_value)

    def test_get_suite_name_from_command_fail(self):
        test_command = ''
        return_value = collector.get_suite_name_from_command(test_command)
        self.assertEqual(test_command, return_value)

    def test_get_suite_name_from_command_raises(self):
        with self.assertRaises(AttributeError):
            collector.get_suite_name_from_command(None)


class GetCaseNameFromCommandTestCase(unittest.TestCase):
    def test_get_case_name_from_command(self):
        test_command = '1:1.1'
        return_value = collector.get_case_name_from_command(test_command)
        self.assertEqual('1', return_value)

    def test_get_case_name_from_command_falsy_return(self):
        test_command = '111'
        return_value = collector.get_case_name_from_command(test_command)
        self.assertIsNone(return_value)

    def test_get_case_name_from_command_full_name(self):
        test_command = '1:11..11'
        return_value = collector.get_case_name_from_command(test_command)
        self.assertEqual('11..11', return_value)

    def test_get_test_name_from_command_value_error(self):
        test_command = '1:11..11'
        return_value = collector.get_test_name_from_command(test_command)
        self.assertIsNone(return_value)

    def test_get_case_name_from_command_raises(self):
        with self.assertRaises(AttributeError):
            collector.get_case_name_from_command(None)


class GetTestNameFromCommandTestCase(unittest.TestCase):
    def test_get_test_name_from_command(self):
        test_command = '1:1.1'
        return_value = collector.get_test_name_from_command(test_command)
        self.assertEqual('1', return_value)

    def test_get_test_name_from_command_falsy_return(self):
        test_command = '111'
        return_value = collector.get_test_name_from_command(test_command)
        self.assertIsNone(return_value)

    def test_get_test_name_from_command_raises(self):
        with self.assertRaises(AttributeError):
            collector.get_test_name_from_command(None)


class TryApplyRulesTestCase(unittest.TestCase):
    try_apply_rules_patch = compose_decorators(
        patch.object(suite.Suite, 'assign_build_rule'))

    def setUp(self):
        self.fake_rule_1 = suite.BuildRule('package.cool_module')
        self.fake_rule_2 = suite.BuildRule('package.cool_module')
        self.fake_rule_01 = suite.BuildRule('package.cool_module01')

        self.different_packages_rules = [
            self.fake_rule_1,
            self.fake_rule_2,
            self.fake_rule_01
        ]
        self.similar_packages_rules = [self.fake_rule_01]

        self.fake_suite_1 = suite.Suite('package.cool_module')
        self.fake_suite_01 = suite.Suite('package.cool_module01')

    @try_apply_rules_patch
    def test_try_apply_rules_similar_packages(self, assign_build):
        collector.try_apply_rules(
            self.fake_suite_01, self.similar_packages_rules)
        assign_build.assert_called_with(self.fake_rule_01)
        self.assertEqual(self.similar_packages_rules, list())

    @try_apply_rules_patch
    def test_try_apply_rules_different_packages(self, assign_build):
        collector.try_apply_rules(
            self.fake_suite_1, self.different_packages_rules)
        self.assertListEqual(
            assign_build.call_args_list,
            [mock.call(self.fake_rule_2), mock.call(self.fake_rule_1)])
        self.assertEqual(self.similar_packages_rules, [self.fake_rule_01])

    @try_apply_rules_patch
    def test_try_apply_rules_empty_suite(self, assign_build):
        collector.try_apply_rules(
            suite_factory.create(), self.different_packages_rules)
        assign_build.assert_not_called()

    @try_apply_rules_patch
    def test_try_apply_rules_empty_rules(self, assign_build):
        collector.try_apply_rules(self.fake_suite_1, [])
        assign_build.assert_not_called()


class TestBaseGenerator(unittest.TestCase):
    base_generator_patch = compose_decorators(
        patch.object(collector, 'call_to_chain'),
        patch.object(collector.extensions, 'clear'),
        patch.object(collector, 'get_shuffle'))

    def setUp(self, *args):
        self.fake_suite = suite_factory.create()

    @base_generator_patch
    def test_base_generator(self, get_shuffle, clear, call_to_chain):
        return_value = collector.base_generator([self.fake_suite]).next()
        self.assertEqual(return_value, self.fake_suite)
        get_shuffle.assert_not_called()
        call_to_chain.assert_called_once()
        clear.assert_called_once()

    @base_generator_patch
    def test_base_generator_with_shuffle(self, get_shuffle, clear, call_to_chain):
        return_value = collector.base_generator(
            [self.fake_suite], shuffle=get_shuffle).next()
        self.assertEqual(return_value, self.fake_suite)
        get_shuffle.assert_called_once()
        call_to_chain.assert_called_once()
        clear.assert_called_once()

    @base_generator_patch
    def test_base_generator_empty_param(self, get_shuffle, clear, call_to_chain):
        funny_string = 'want2passaword'
        return_value = ''.join(
            x for x in collector.base_generator(funny_string))
        self.assertEqual(funny_string, return_value)
        call_to_chain.assert_called_once()
        clear.assert_called_once()


class GetGeneratorByCommandsTestCase(unittest.TestCase):
    generator_by_commands_patch = compose_decorators(
        patch.object(collector, 'call_to_chain'),
        patch.object(collector.extensions, 'clear'),
        patch.object(loader, 'load_suite_by_name'))

    def setUp(self):
        self.fake_rule_a = suite.BuildRule('a', case_name='b', test_name='c')
        self.fake_rule_b = suite.BuildRule('x', case_name='y', test_name='z')
        self.rules = [self.fake_rule_a, self.fake_rule_b]

    @generator_by_commands_patch
    @patch.object(collector, 'try_apply_rules', side_effect=mock_try_apply_rules)
    def test_generator_by_commands(
            self,
            try_apply_rules,
            load_suite_by_name,
            clear,
            call_to_chain):
        answers_list = []
        for resp in collector.generator_by_commands([], self.rules):
            answers_list.append(resp)
        self.assertEqual(answers_list, [loader.load_suite_by_name()])
        self.assertEqual(try_apply_rules.call_count, 2)
        self.assertEqual(load_suite_by_name.call_count, 3)
        call_to_chain.assert_called_once()
        clear.assert_called_once()

    @generator_by_commands_patch
    @patch.object(collector, 'try_apply_rules')
    def test_generator_by_commands_raises(
            self,
            try_apply_rules,
            load_suite_by_name,
            clear,
            call_to_chain):
        with self.assertRaises(exceptions.CollectError):
            collector.generator_by_commands([], self.rules).next()
        call_to_chain.assert_not_called()
        clear.assert_not_called()
        self.assertEqual(try_apply_rules.call_count, 2)
        self.assertEqual(load_suite_by_name.call_count, 2)

    def test_generator_by_commands_with_shuffle(self):
        shuffle_mock = mock.Mock(callable=True)
        for _ in collector.generator_by_commands([], [], shuffle=shuffle_mock):
            pass
        shuffle_mock.assert_called_once()


class CreateGeneratorTestCase(unittest.TestCase):
    create_generator_patch = compose_decorators(
        patch.object(collector, 'get_shuffle'),
        patch.object(collector, 'get_suite_name_from_command'),
        patch.object(collector, 'get_case_name_from_command'),
        patch.object(collector, 'get_test_name_from_command'))

    @create_generator_patch
    @patch.object(collector, 'generator_by_commands', return_value='generator_by_comms')
    def test_create_generator(
            self,
            generator_by_commands,
            get_test_name_from_command,
            get_case_name_from_command,
            get_suite_name_from_command,
            get_shuffle):
        fake_config = config_factory.create(**{'TESTS': ['one:two.three']})
        return_value = collector.create_generator([], fake_config)
        self.assertEqual(return_value, 'generator_by_comms')
        generator_by_commands.assert_called_once()
        get_test_name_from_command.assert_called_once()
        get_case_name_from_command.assert_called_once()
        get_suite_name_from_command.assert_called_once()
        get_shuffle.assert_called_once()

    @create_generator_patch
    @patch.object(collector, 'base_generator', return_value='base_generator')
    def test_create_generator_no_tests_param(
            self,
            base_generator,
            get_test_name_from_command,
            get_case_name_from_command,
            get_suite_name_from_command,
            get_shuffle):
        fake_config = config_factory.create()
        return_value = collector.create_generator([], fake_config)
        self.assertEqual(return_value, 'base_generator')
        base_generator.assert_called_once()
        get_test_name_from_command.assert_not_called()
        get_case_name_from_command.assert_not_called()
        get_suite_name_from_command.assert_not_called()
        get_shuffle.assert_called_once()

    def test_create_generator_empty_config(self):
        with self.assertRaises(AttributeError):
            collector.create_generator([], [])
