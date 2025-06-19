#!/usr/bin/env python3
"""
L5X Functional Equivalence Comparison Script

Usage:
    python l5x_compare.py original.L5X roundtrip.L5X

Compares tags, programs, routines, data types, and function blocks.
"""
import sys
import l5x
from collections import defaultdict

def extract_tags(prj):
    tags = {}
    if hasattr(prj, 'controller') and prj.controller is not None:
        if hasattr(prj.controller, 'tags') and prj.controller.tags is not None:
            for tag in prj.controller.tags.names:
                try:
                    tag_obj = prj.controller.tags[tag]
                    # Try different ways to get the data type
                    data_type = ''
                    if hasattr(tag_obj, 'DataType'):
                        data_type = tag_obj.DataType
                    elif hasattr(tag_obj, 'dataType'):
                        data_type = tag_obj.dataType
                    elif hasattr(tag_obj, 'getAttribute'):
                        data_type = tag_obj.getAttribute('DataType', '')
                    tags[tag] = data_type
                except Exception as e:
                    print(f"  Warning: Could not process tag '{tag}': {e}")
                    tags[tag] = 'ERROR'
    return tags

def extract_programs(prj):
    programs = {}
    if hasattr(prj, 'programs') and prj.programs is not None:
        for prog in prj.programs.names:
            try:
                prog_obj = prj.programs[prog]
                routines = {}
                if hasattr(prog_obj, 'routines') and prog_obj.routines is not None:
                    for routine in prog_obj.routines.names:
                        try:
                            routine_obj = prog_obj.routines[routine]
                            # Try different ways to get the routine type
                            routine_type = ''
                            if hasattr(routine_obj, 'Type'):
                                routine_type = routine_obj.Type
                            elif hasattr(routine_obj, 'type'):
                                routine_type = routine_obj.type
                            elif hasattr(routine_obj, 'getAttribute'):
                                routine_type = routine_obj.getAttribute('Type', '')
                            routines[routine] = routine_type
                        except Exception as e:
                            print(f"  Warning: Could not process routine '{routine}' in program '{prog}': {e}")
                            routines[routine] = 'ERROR'
                programs[prog] = routines
            except Exception as e:
                print(f"  Warning: Could not process program '{prog}': {e}")
                programs[prog] = {}
    return programs

def extract_data_types(prj):
    types = set()
    if hasattr(prj, 'controller') and prj.controller is not None:
        if hasattr(prj.controller, 'datatypes') and prj.controller.datatypes is not None:
            for dtype in prj.controller.datatypes.names:
                types.add(dtype)
    return types

def extract_function_blocks(prj):
    fbs = set()
    if hasattr(prj, 'controller') and prj.controller is not None:
        if hasattr(prj.controller, 'functionblocks') and prj.controller.functionblocks is not None:
            for fb in prj.controller.functionblocks.names:
                fbs.add(fb)
    return fbs

def print_diff(title, only_in_a, only_in_b, label_a, label_b):
    if only_in_a:
        print(f"  {title} only in {label_a}:")
        for item in sorted(only_in_a):
            print(f"    {item}")
    if only_in_b:
        print(f"  {title} only in {label_b}:")
        for item in sorted(only_in_b):
            print(f"    {item}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python l5x_compare.py original.L5X roundtrip.L5X")
        sys.exit(1)
    orig_path, rt_path = sys.argv[1], sys.argv[2]
    print(f"Comparing:\n  Original:   {orig_path}\n  Roundtrip:  {rt_path}\n")
    orig = l5x.Project(orig_path)
    rt = l5x.Project(rt_path)

    # Tags
    orig_tags = extract_tags(orig)
    rt_tags = extract_tags(rt)
    print("Tags:")
    print_diff("Tags", set(orig_tags.keys()) - set(rt_tags.keys()), set(rt_tags.keys()) - set(orig_tags.keys()), "original", "roundtrip")
    # Compare tag types
    common_tags = set(orig_tags.keys()) & set(rt_tags.keys())
    type_mismatches = [(t, orig_tags[t], rt_tags[t]) for t in common_tags if orig_tags[t] != rt_tags[t]]
    if type_mismatches:
        print("  Tag type mismatches:")
        for t, otype, rtype in type_mismatches:
            print(f"    {t}: original={otype}, roundtrip={rtype}")
    if not (set(orig_tags.keys()) - set(rt_tags.keys()) or set(rt_tags.keys()) - set(orig_tags.keys()) or type_mismatches):
        print("  ✓ Tags match")

    # Programs and routines
    orig_progs = extract_programs(orig)
    rt_progs = extract_programs(rt)
    print("\nPrograms and Routines:")
    print_diff("Programs", set(orig_progs.keys()) - set(rt_progs.keys()), set(rt_progs.keys()) - set(orig_progs.keys()), "original", "roundtrip")
    common_progs = set(orig_progs.keys()) & set(rt_progs.keys())
    for prog in common_progs:
        orig_routines = orig_progs[prog]
        rt_routines = rt_progs[prog]
        print_diff(f"Routines in program {prog}", set(orig_routines.keys()) - set(rt_routines.keys()), set(rt_routines.keys()) - set(orig_routines.keys()), "original", "roundtrip")
        # Compare routine types
        common_routines = set(orig_routines.keys()) & set(rt_routines.keys())
        routine_type_mismatches = [(r, orig_routines[r], rt_routines[r]) for r in common_routines if orig_routines[r] != rt_routines[r]]
        if routine_type_mismatches:
            print(f"  Routine type mismatches in program {prog}:")
            for r, otype, rtype in routine_type_mismatches:
                print(f"    {r}: original={otype}, roundtrip={rtype}")
    if not (set(orig_progs.keys()) - set(rt_progs.keys())) and not (set(rt_progs.keys()) - set(orig_progs.keys())):
        print("  ✓ Programs match")

    # Data types
    orig_types = extract_data_types(orig)
    rt_types = extract_data_types(rt)
    print("\nUser Data Types:")
    print_diff("Data types", orig_types - rt_types, rt_types - orig_types, "original", "roundtrip")
    if not (orig_types - rt_types or rt_types - orig_types):
        print("  ✓ Data types match")

    # Function blocks
    orig_fbs = extract_function_blocks(orig)
    rt_fbs = extract_function_blocks(rt)
    print("\nFunction Blocks:")
    print_diff("Function blocks", orig_fbs - rt_fbs, rt_fbs - orig_fbs, "original", "roundtrip")
    if not (orig_fbs - rt_fbs or rt_fbs - orig_fbs):
        print("  ✓ Function blocks match")

    print("\nComparison complete.")

if __name__ == "__main__":
    main() 