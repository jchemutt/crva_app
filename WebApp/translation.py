from modeltranslation.translator import register, TranslationOptions
from .models import (
    ValueChain, Component, Hazard, Stage,
    Risk, AdaptationStrategy, ImplementationStrategy, ImplementationEntry
)

@register(ValueChain)
class ValueChainTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Component)
class ComponentTranslationOptions(TranslationOptions):
    fields = ('label',)

@register(Hazard)
class HazardTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Stage)
class StageTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Risk)
class RiskTranslationOptions(TranslationOptions):
    fields = ('description',)

@register(AdaptationStrategy)
class AdaptationStrategyTranslationOptions(TranslationOptions):
    fields = ('description',)

@register(ImplementationStrategy)
class ImplementationStrategyTranslationOptions(TranslationOptions):
    fields = ('title',)

@register(ImplementationEntry)
class ImplementationEntryTranslationOptions(TranslationOptions):
    fields = (
        'proposed_activities',
        'timeframe',
        'implementers',
        'resources_needed',
        'expected_outcomes',
        'beneficiaries',
    )
