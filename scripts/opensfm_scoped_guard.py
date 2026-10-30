"""Reject modes needing omitted vocabulary assets in the scoped local runtime."""


def validate_config(config: dict) -> None:
    matcher = config.get('matcher_type')
    bow = config.get('matching_bow_neighbors')
    vlad = config.get('matching_vlad_neighbors')
    if not isinstance(matcher, str) or type(bow) is not int or type(vlad) is not int or bow < 0 or vlad < 0:
        raise ValueError('Scoped OpenSfM invalid matching configuration')
    if matcher.upper() == 'WORDS' or bow > 0 or vlad > 0:
        raise ValueError('Scoped OpenSfM: BoW/WORDS matching and VLAD retrieval are not supported; vocabulary assets are omitted')
