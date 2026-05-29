<div align="center">
  <img src="DOCUMENTS/images/text_logo.png" alt="Agent_X" />
</div>

# Agent_X

Agent_X is organized into three visible layers:

- **L0**: governed universal seed kernel
- **L1**: external evolution/controller layer
- **L2**: specialization profiles and integration blueprints

## Quick start

```
make install
make seed-boot
make prove-seed
make run
```

## Layer map

- [L0/README.md](L0/README.md) — L0 seed kernel documentation
- [L1/README.md](L1/README.md) — L1 evolution controller documentation
- [L2/README.md](L2/README.md) — L2 specialization documentation

## Visual Guide

<div align="center">
  <img src="DOCUMENTS/images/agent_x_01_high_level_flow.png" alt="High-Level Flow" width="450" />
</div>

See [DOCUMENTS/images/](DOCUMENTS/images/) for the full set of visual guides.

## Commands

| Command | Purpose |
|---|---|
| `make install` | Install minimal seed dependencies |
| `make seed-boot` | Compile and boot the seed |
| `make prove-seed` | Run canonical L0 seed proof |
| `make run` | Run one default seed turn |
| `make build-seed` | Build seed package from manifest |
| `make prove-l1` | Run L1 structure tests |
| `make prove-l2` | Run L2 structure tests |
| `make prove-all` | Run all tests across layers |
| `make clean` | Remove generated runtime artifacts |

## License

Proprietary — see [LICENSE](LICENSE).
