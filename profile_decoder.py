import time
import stim
import numpy as np
from src.asr_mp.decoder import TesseractCompiledDecoder

# Generate d=5 circuit
circuit = stim.Circuit.generated(
    "surface_code:rotated_memory_z",
    distance=5,
    rounds=15,
    after_clifford_depolarization=0.004
)
dem = circuit.detector_error_model(decompose_errors=True)

print("Compiling decoder...")
t0 = time.time()
decoder = TesseractCompiledDecoder(dem)
print(f"Compilation took {time.time()-t0:.4f}s")

# Generate 10 shots
print("Generating shots...")
sampler = circuit.compile_detector_sampler()
shots = sampler.sample(10, append_observables=False)
packed_shots = np.packbits(shots, axis=1, bitorder='little')

print("Decoding 10 shots...")
t0 = time.time()
decoder.decode_shots_bit_packed(bit_packed_detection_event_data=packed_shots)
params = f"MaxIter={decoder.decoder.max_iter}, OSD={decoder.decoder.osd_order}"
print(f"Decoding 10 shots took {time.time()-t0:.4f}s ({params})")
