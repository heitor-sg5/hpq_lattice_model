def validate_sequence(seq, residue_props):
    """Validate a peptide sequence against known residue types."""
    seq = seq.strip().upper()
    if not seq:
        return "Sequence cannot be empty."
    unknown = {aa for aa in seq if aa not in residue_props}
    if unknown:
        return f"Unknown residue types in sequence: {', '.join(sorted(unknown))}"
    return None