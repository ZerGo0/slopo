package pipeline;

import java.util.List;
import java.util.function.Function;
import java.util.stream.Collectors;

public class Processor {
    private Runnable onComplete;

    public List<Integer> transform(List<Integer> values) {
        Function<Integer, Integer> doubler = x -> x * 2;
        return values.stream()
                .filter(v -> v > 0)
                .map(v -> {
                    int scaled = doubler.apply(v);
                    return scaled + 1;
                })
                .collect(Collectors.toList());
    }

    public void configure() {
        this.onComplete = () -> {
            System.out.println("done");
        };
    }

    public Function<String, String> createTrimmer() {
        return text -> text.trim();
    }
}
