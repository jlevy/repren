# Essential Testing Guidelines

## 1. Test Real System Interactions, Not Mock Existence

** Don’t test that mocks were created correctly:**
```typescript
it('should have all required methods', () => {
  const mockService = createMockService();
  expect(typeof mockService.process).toBe('function');
});
```

** Test actual system behavior with dependencies:**
```typescript
it('should process data through the pipeline', async () => {
  const mockDatabase = createMockDatabase();
  const processor = new DataProcessor(mockDatabase);

  await processor.handle(inputData);

  expect(mockDatabase.save).toHaveBeenCalledWith(
    expect.objectContaining({ processed: true })
  );
});
```

## 2. Test Integration Points and Data Flow

** Don’t test isolated dependency calls:**
```typescript
await mockService.call('parameter');
expect(mockService.call).toHaveBeenCalledWith('parameter');
```

** Test data flow between components:**
```typescript
it('should transform data correctly between services', async () => {
  const mockTransformer = createMockTransformer();
  const mockStorage = createMockStorage();
  const pipeline = new DataPipeline(mockTransformer, mockStorage);

  await pipeline.process(rawData);

  expect(mockTransformer.transform).toHaveBeenCalledWith(rawData);
  expect(mockStorage.store).toHaveBeenCalledWith(
    expect.objectContaining({ transformed: true })
  );
});
```

## 3. Test Error Scenarios and Edge Cases

** Don’t only test happy path scenarios:**
```typescript
it('should handle success case', async () => {
  await service.process(validData);
  expect(mockDependency.save).toHaveBeenCalled();
});
```

** Test error handling and recovery:**
```typescript
it('should retry when external service fails', async () => {
  const mockApi = vi.fn()
    .mockRejectedValueOnce(new Error('Network error'))
    .mockResolvedValueOnce({ success: true });

  const service = new ExternalService(mockApi);
  const result = await service.fetchWithRetry();

  expect(mockApi).toHaveBeenCalledTimes(2);
  expect(result.success).toBe(true);
});
```

## 4. Structure Tests Around Business Scenarios

** Don’t organize by technical components:**
```typescript
describe('Database interface', () => {
  // Tests about database methods
});
```

** Organize by business workflows:**
```typescript
describe('Order processing workflow', () => {
  describe('when payment succeeds', () => {
    it('should update inventory');
    it('should send confirmation email');
    it('should schedule delivery');
  });

  describe('when payment fails', () => {
    it('should preserve cart contents');
    it('should notify user of failure');
  });
});
```

## 5. Validate Data Quality and Contract Compliance

** Don’t just verify that interactions happened:**
```typescript
expect(mockService.process).toHaveBeenCalled();
```

** Validate that data contracts are respected:**
```typescript
it('should pass complete user profile to recommendation engine', async () => {
  const mockRecommendations = createMockRecommendationService();
  const userService = new UserService(mockRecommendations);

  await userService.getRecommendations(userId);

  expect(mockRecommendations.generate).toHaveBeenCalledWith(
    expect.objectContaining({
      userId: expect.any(String),
      preferences: expect.any(Array),
      history: expect.any(Array),
      demographics: expect.any(Object)
    })
  );
});
```

**Key Takeaway:** Integration tests should verify that components work together
correctly by testing real interactions, data flow, error handling, business scenarios,
and data contracts—not just that mocks exist or methods are called.
