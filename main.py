import os
import sys
import argparse
import shutil
import tempfile
from pathlib import Path

try:
    import pyghidra
except ImportError:
    pyghidra = None

def decompile_executable(executable_path, output_path=None, analyze=True, verbose=False, cleanup=True):
    pyghidra.start(verbose=verbose)
    
    from ghidra.app.decompiler import DecompInterface
    from ghidra.util.task import ConsoleTaskMonitor
    
    executable_path = Path(executable_path).resolve()
    
    if not output_path:
        output_path = executable_path.with_suffix('.c')
    else:
        output_path = Path(output_path).resolve()
        if output_path.is_dir():
            executable_name = executable_path.name
            output_path = output_path / f"{executable_name}.c"
            
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if verbose:
        print(f"Decompiling {executable_path}")
        print(f"Output will be saved to {output_path}")
    
    temp_dir = None
    if cleanup:
        temp_dir = tempfile.mkdtemp(prefix="ghidra_")
        project_location = temp_dir
        project_name = "temp_project"
    else:
        project_location = None
        project_name = None
    
    try:
        with pyghidra.open_program(executable_path, project_name=project_name, 
                                  project_location=project_location, analyze=analyze) as flat_api:
            program = flat_api.getCurrentProgram()
            monitor = ConsoleTaskMonitor()
            
            if verbose:
                print(f"Program loaded: {program.getName()}")
                print(f"Architecture: {program.getLanguage().getProcessor().toString()}")
            
            decompiler = DecompInterface()
            decompiler.openProgram(program)
            
            function_manager = program.getFunctionManager()
            functions = list(function_manager.getFunctions(True))
            
            if verbose:
                print(f"Found {len(functions)} functions")
            
            with open(output_path, 'w') as f:
                f.write(f"// Decompiled using PyGhidra\n")
                f.write(f"// Program: {program.getName()}\n")
                f.write(f"// Architecture: {program.getLanguage().getProcessor().toString()}\n\n")
                
                successful = 0
                for function in functions:
                    if function.isExternal():
                        continue
                    
                    if verbose:
                        print(f"Decompiling: {function.getName()} @ {function.getEntryPoint()}")
                    
                    results = decompiler.decompileFunction(function, 60, monitor)
                    
                    if results.decompileCompleted():
                        f.write(f"// Function: {function.getName()}\n")
                        f.write(f"// Address: {function.getEntryPoint()}\n")
                        f.write(f"{results.getDecompiledFunction().getC()}\n\n")
                        successful += 1
                    else:
                        f.write(f"// Failed to decompile: {function.getName()}\n\n")
                
                if verbose:
                    print(f"Successfully decompiled {successful} out of {len(functions)} functions")
    
    finally:
        if cleanup and temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                if verbose:
                    print(f"Removed temporary project directory: {temp_dir}")
            except Exception as e:
                if verbose:
                    print(f"Warning: failed to clean up temp directory: {e}")
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Decompile executables using PyGhidra")
    parser.add_argument("executable", help="Path to the executable file to decompile")
    parser.add_argument("output", nargs="?", help="Output file path (default: same as input with .c extension)")
    parser.add_argument("--no-analyze", action="store_true", help="Skip Ghidra's analysis phase")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--no-cleanup", action="store_true", help="Keep temporary Ghidra project files")
    
    args = parser.parse_args()
    
    try:
        if pyghidra is None:
            print("PyGhidra is not installed. Please install it with:")
            print("  pip install pyghidra")
            print("And ensure GHIDRA_INSTALL_DIR environment variable is set")
            sys.exit(1)
        
        output_file = decompile_executable(
            args.executable,
            args.output,
            analyze=not args.no_analyze,
            verbose=args.verbose,
            cleanup=not args.no_cleanup
        )
        
        print(f"Decompilation complete. Output saved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()