from psychopy.experiment.exports import IndentingBuffer
from . import _TestBaseComponentsMixin, _TestDisabledMixin
from psychopy import experiment
import inspect


class _Generic(_TestBaseComponentsMixin, _TestDisabledMixin):
    def __init__(self, compClass):
        self.exp = experiment.Experiment()
        self.rt = experiment.routines.Routine(exp=self.exp, name="testRoutine")
        self.exp.addRoutine("testRoutine", self.rt)
        self.exp.flow.addRoutine(self.rt, 0)
        self.comp = compClass(exp=self.exp, parentName="testRoutine", name=f"test{compClass.__name__}")
        self.rt.addComponent(self.comp)


def test_all_components():
    for compName, compClass in experiment.getAllComponents().items():
        if compName == "SettingsComponent":
            continue
        # Make a generic testing object for this component
        tester = _Generic(compClass)
        # Run each method from _TestBaseComponentsMixin on tester
        for attr, meth in _TestBaseComponentsMixin.__dict__.items():
            if inspect.ismethod(meth):
                meth(tester)
        # Run each method from _TestBaseComponentsMixin on tester
        for attr, meth in _TestDisabledMixin.__dict__.items():
            if inspect.ismethod(meth):
                meth(tester)


def test_indentation_consistency():
    """
    No component should exit any of its write methods at a different indent level as it entered, as this would break
    subsequent components / routines.
    """
    for compName, compClass in experiment.getAllComponents().items():
        if compName == "SettingsComponent":
            continue
        # Make a generic testing object for this component
        tester = _Generic(compClass)
        # Skip if component doesn't have a start/stop time
        if "startVal" not in tester.comp.params or "stopVal" not in tester.comp.params:
            continue
        # Check that each write method exits at the same indent level as it entered
        buff = IndentingBuffer(target="PsychoPy")
        msg = "Writing {} code for {} changes indent level by {} when start is `{}` and stop is `{}`."
        # Setup flow for writing
        tester.exp.flow.writeStartCode(buff)
        # Try combinations of start/stop being set/unset
        cases = [
            {"startVal": "0", "stopVal": "1"},
            {"startVal": "", "stopVal": "1"},
            {"startVal": "0", "stopVal": ""},
            {"startVal": "", "stopVal": ""},
        ]
        for case in cases:
            tester.comp.params["startType"].val = "time (s)"
            tester.comp.params["stopType"].val = "time (s)"
            for param, val in case.items():
                tester.comp.params[param].val = val
            # Init
            tester.comp.writeInitCode(buff)
            assert buff.indentLevel == 0, msg.format(
                "init", type(tester.comp).__name__, buff.indentLevel, case['startVal'], case['stopVal']
            )
            # Start routine
            tester.comp.writeRoutineStartCode(buff)
            assert buff.indentLevel == 0, msg.format(
                "routine start", type(tester.comp).__name__, buff.indentLevel, case['startVal'], case['stopVal']
            )
            # Each frame
            tester.comp.writeFrameCode(buff)
            assert buff.indentLevel == 0, msg.format(
                "each frame", type(tester.comp).__name__, buff.indentLevel, case['startVal'], case['stopVal']
            )
            # End routine
            tester.comp.writeRoutineEndCode(buff)
            assert buff.indentLevel == 0, msg.format(
                "routine end", type(tester.comp).__name__, buff.indentLevel, case['startVal'], case['stopVal']
            )
            # End experiment
            tester.comp.writeExperimentEndCode(buff)
            assert buff.indentLevel == 0, msg.format(
                "experiment end", type(tester.comp).__name__, buff.indentLevel, case['startVal'], case['stopVal']
            )
