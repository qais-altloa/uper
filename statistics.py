
def show(results, player_name=""):
    if not results:
        print("\n📊 No trip data to analyze.")
        return

    sep = "=" * 60

    print("\n" + sep)
    print("📊  TRIP STATISTICS" + (f"  —  {player_name}" if player_name else ""))
    print(sep)

    # ── collect data ──────────────────────────────────────────────────────────
    costs       = [r['cost']           for r in results]
    times       = [r['time']           for r in results]
    distances   = [r['total_distance'] for r in results]
    drivers     = [r['driver']         for r in results]
    algos       = [r['request'].id     for r in results]   # just to count trips

    # ── averages ──────────────────────────────────────────────────────────────
    avg_cost = sum(costs)     / len(costs)
    avg_time = sum(times)     / len(times)
    avg_dist = sum(distances) / len(distances)

    print(f"\n  📈 Averages")
    print(f"     Cost     : {avg_cost:.1f} EGP")
    print(f"     Time     : {avg_time:.1f} min")
    print(f"     Distance : {avg_dist:.1f} steps")

    # ── extremes ──────────────────────────────────────────────────────────────
    most_expensive = max(results, key=lambda r: r['cost'])
    cheapest       = min(results, key=lambda r: r['cost'])
    fastest        = min(results, key=lambda r: r['time'])
    longest        = max(results, key=lambda r: r['total_distance'])

    print(f"\n  💰 Most Expensive Trip")
    print(f"     Trip {most_expensive['request'].id}  →  {most_expensive['cost']} EGP"
          f"  |  Driver: {most_expensive['driver'].name}")

    print(f"\n  🏷️  Cheapest Trip")
    print(f"     Trip {cheapest['request'].id}  →  {cheapest['cost']} EGP"
          f"  |  Driver: {cheapest['driver'].name}")

    print(f"\n  ⚡ Fastest Trip")
    print(f"     Trip {fastest['request'].id}  →  {fastest['time']} min"
          f"  |  Driver: {fastest['driver'].name}")

    print(f"\n  📏 Longest Distance")
    print(f"     Trip {longest['request'].id}  →  {longest['total_distance']} steps"
          f"  |  Driver: {longest['driver'].name}")

    # ── busiest driver ────────────────────────────────────────────────────────
    from collections import Counter
    driver_counts = Counter(r['driver'].name for r in results)
    busiest_name, busiest_count = driver_counts.most_common(1)[0]

    print(f"\n  🚗 Busiest Driver")
    print(f"     {busiest_name}  →  {busiest_count} trip(s)")

    # ── totals ────────────────────────────────────────────────────────────────
    print(f"\n  🧾 Session Totals")
    print(f"     Trips completed : {len(results)}")
    print(f"     Total cost      : {sum(costs)} EGP")
    print(f"     Total time      : {sum(times)} min")
    print(f"     Total distance  : {sum(distances)} steps")

    print("\n" + sep + "\n")
