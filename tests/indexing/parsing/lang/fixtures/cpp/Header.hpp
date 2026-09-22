#pragma once

template <typename T>
T clamp(T value, T lo, T hi) {
    T low_bounded = value < lo ? lo : value;
    return low_bounded > hi ? hi : low_bounded;
}

class Counter {
public:
    Counter() : count_(0) {}

    void increment() {
        count_ += 1;
        doubled_ = count_ * 2;
    }

    int value() const {
        return count_;
    }

private:
    int count_;
    int doubled_;
};
