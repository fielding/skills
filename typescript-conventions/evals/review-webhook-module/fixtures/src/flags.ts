/** Feature flags load asynchronously after the profile; undefined while loading. */
export function useFeatureFlag(name: string): boolean | undefined {
  // Real implementation reads the flag store; stubbed for review.
  void name;
  return undefined;
}
