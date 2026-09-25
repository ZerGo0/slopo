std::string load(const std::string &path) {
    try {
        std::string raw = fetch(path);
        std::string trimmed = trim(raw);
        return trimmed;
    } catch (const std::out_of_range &e) {
        log(e.what());
        return "";
    } catch (const std::exception &e) {
        log(e.what());
        throw;
    }
    return "";
}
