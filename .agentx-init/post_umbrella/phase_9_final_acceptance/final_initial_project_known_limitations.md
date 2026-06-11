# Known Limitations

1. **Agents created manually**: Clothing advice and daily planning agents were created manually, not through the governed patching pipeline. Provenance artifacts for governed generation do not exist.
2. **Governance benchmark B019 (claims)**: Tests that `create_gate_decision` rejects invalid claims, but the `release_claims` field is not validated by the promotion gate policy itself. The check operates at the `is_promotion_approved` level.
3. **Addendum A-H not implemented**: The Revision 3 Hardening Addendum (sections A through H) has not been implemented. See `3_agent_x_post_umbrella_next_phase_llm_prompt_10_10_rev3.md` lines 1157-1335.
4. **No temporary-directory replay**: Clean-checkout replay has not been verified in a separate temporary clone.
5. **No capability matrix**: The per-agent capability least-privilege matrix (Addendum C) does not exist.
6. **LLM dependency**: Integration and system tests require a running opencode server at `http://127.0.0.1:14096`.
